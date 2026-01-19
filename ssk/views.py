# ssk/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Tag
from .forms import PostForm
from django.db.models import Count
from types import SimpleNamespace
from datetime import timedelta

def post_list(request):
    # 複数タグ選択対応 + AND/OR 切替
    tag_ids = []
    for t in request.GET.getlist("tag"):
        try:
            tag_ids.append(int(t))
        except (TypeError, ValueError):
            pass

    mode = request.GET.get("mode", "and")  # "and" または "or"
    posts = Post.objects.prefetch_related("tags").order_by("date")

    if tag_ids:
        if mode == "or":
            posts = posts.filter(tags__id__in=tag_ids).distinct()
        else:  # "and"（デフォルト）
            for tid in tag_ids:
                posts = posts.filter(tags__id=tid)

    selected_tag_ids = tag_ids  # テンプレートでチェックの判定に使う
    selected_mode = mode
    # order tags by usage (post count) desc, then name
    tags = Tag.objects.annotate(num_posts=Count("posts")).order_by("-num_posts", "name")

    # 分割: 日付あり / 日付なし をテンプレートで別表示できるようにする
    dated_posts = posts.filter(date__isnull=False).order_by("date", "created_at")
    undated_posts = posts.filter(date__isnull=True).order_by("-created_at")

    # Assign a color index to each post interval so overlapping intervals get different colors.
    # Greedy coloring: keep track of last end date for each color, reuse color when it does not overlap.
    post_color = {}
    color_ends = []  # list of end dates per color
    # Build list of unique posts with intervals, sorted by start date
    intervals = []
    for p in dated_posts:
        start = p.date
        end = p.end_date if getattr(p, "end_date", None) else start
        if end is None or end < start:
            end = start
        intervals.append((p, start, end))
    intervals.sort(key=lambda x: (x[1], x[2] or x[1], x[0].created_at))

    for (p, start, end) in intervals:
        # find a color whose last end is < start (no overlap)
        assigned = None
        for idx, last_end in enumerate(color_ends):
            if last_end < start:
                assigned = idx
                color_ends[idx] = end
                break
        if assigned is None:
            assigned = len(color_ends)
            color_ends.append(end)
        post_color[p.pk] = assigned

    # Expand ranged posts into entries for each date in their interval, attach color_index
    expanded_posts = []
    for post in dated_posts:
        start = post.date
        end = post.end_date if getattr(post, "end_date", None) else start
        # if end_date is before start, treat as single day
        if end is None or end < start:
            end = start
        d = start
        is_range = (end > start)
        # color index (default 0 if not assigned)
        color_idx = post_color.get(post.pk, 0)
        while d <= end:
            expanded_posts.append(SimpleNamespace(display_date=d, post=post, is_range=is_range, color_index=color_idx))
            d += timedelta(days=1)

    # sort entries by display_date, with range entries shown first,
    # then by post.start date / created_at to keep a stable order
    expanded_posts.sort(key=lambda e: (
        e.display_date,
        0 if e.is_range else 1,                 # range entries first
        e.post.date or e.post.created_at,
        e.post.created_at
    ))

    return render(request, "teams/ssk/post_list.html", {
        "dated_posts": dated_posts,           # original queryset (kept if needed)
        "expanded_posts": expanded_posts,     # flattened entries for per-day display
        "undated_posts": undated_posts,
        "tags": tags,
        "selected_tag_ids": selected_tag_ids,
        "selected_mode": selected_mode,
    })


def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            # date (start) + optional end_date saved separately
            post = Post(
                title=form.cleaned_data["title"],
                date=form.cleaned_data.get("date"),
                end_date=form.cleaned_data.get("end_date"),
                body=form.cleaned_data["body"],
            )
            post.save()

            # set password if provided (only on create)
            pwd = form.cleaned_data.get("password")
            if pwd:
                post.set_password(pwd)
                post.save()

            # タグ文字列をパースして ManyToMany に紐づけ (既存処理)
            tags_text = form.cleaned_data.get("tags_text", "")
            names = []

            # スペース区切り（全角スペースも対応）
            for raw in tags_text.replace("　", " ").split():
                token = raw.strip()
                # 先頭の # は削る（#授業 → 授業）
                if token.startswith("#"):
                    token = token[1:]
                if token:
                    names.append(token)

            # Tag を作成 or 取得して post に紐づけ
            for name in names:
                tag, created = Tag.objects.get_or_create(name=name)
                post.tags.add(tag)

            return redirect("ssk:post_list")
    else:
        form = PostForm()

    all_tag_names = list(Tag.objects.order_by("name").values_list("name", flat=True))
    return render(request, "teams/ssk/post_form.html", {"form": form, "all_tag_names": all_tag_names})


def post_detail(request, pk):
    """
    Show a single post (イベントの本文を表示).
    """
    post = get_object_or_404(Post.objects.prefetch_related("tags"), pk=pk)
    return render(request, "teams/ssk/post_detail.html", {"post": post})

def post_unlock(request, pk):
    """
    Prompt for password before allowing edit. Sets a session flag when correct.
    """
    post = get_object_or_404(Post, pk=pk)
    # If no password is set, go straight to edit.
    if not post.password_hash:
        return redirect("ssk:post_edit", pk=pk)

    error = None
    if request.method == "POST":
        pwd = request.POST.get("password", "")
        if post.check_password(pwd):
            # mark unlocked in session
            request.session[f"unlocked_post_{pk}"] = True
            # redirect to edit page
            return redirect("ssk:post_edit", pk=pk)
        else:
            error = "パスワードが間違っています。"

    return render(request, "teams/ssk/post_unlock.html", {
        "post": post,
        "error": error,
    })


def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # require unlock if post has a password
    if post.password_hash and not request.session.get(f"unlocked_post_{pk}"):
        return redirect("ssk:post_unlock", pk=pk)

    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post.title = form.cleaned_data["title"]
            post.date = form.cleaned_data.get("date")
            post.end_date = form.cleaned_data.get("end_date")
            post.body = form.cleaned_data["body"]
            post.save()

            # clear the unlock flag after a successful edit (optional)
            try:
                del request.session[f"unlocked_post_{pk}"]
            except KeyError:
                pass

            # タグ文字列をパースして post.tags を更新
            tags_text = form.cleaned_data.get("tags_text", "")
            names = []
            for raw in tags_text.replace("　", " ").split():
                token = raw.strip()
                if token.startswith("#"):
                    token = token[1:]
                if token:
                    names.append(token)

            post.tags.clear()
            for name in names:
                tag, created = Tag.objects.get_or_create(name=name)
                post.tags.add(tag)

            return redirect("ssk:post_detail", pk=post.pk)
    else:
        # 現在のタグから tags_text を事前入力（"#name #name" 形式で表示）
        tags_initial = " ".join("#" + t.name for t in post.tags.all())
        initial = {"tags_text": tags_initial}
        # prefill date/end_date when available
        if post.date is not None:
            initial["date"] = post.date
        if getattr(post, "end_date", None) is not None:
            initial["end_date"] = post.end_date
        form = PostForm(instance=post, initial=initial)

    all_tag_names = list(Tag.objects.order_by("name").values_list("name", flat=True))
    return render(request, "teams/ssk/post_form.html", {"form": form, "post": post, "all_tag_names": all_tag_names})


def post_delete(request, pk):
    """
    Delete a post. Confirm via POST.
    """
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        post.delete()
        return redirect("ssk:post_list")
    # If GET, show detail page (or you can implement a separate confirm page).
    return render(request, "teams/ssk/post_detail.html", {"post": post})
