# ssk/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Tag
from .forms import PostForm

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
    tags = Tag.objects.order_by("name")

    return render(request, "teams/ssk/post_list.html", {
        "posts": posts,
        "tags": tags,
        "selected_tag_ids": selected_tag_ids,
        "selected_mode": selected_mode,
    })


def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)
    
            
        if form.is_valid():
            # ① Post 本体を保存
            post = Post(
                title=form.cleaned_data["title"],
                date=form.cleaned_data["date"],
                body=form.cleaned_data["body"],
            )
            post.save()

            # ② タグ文字列をパースして ManyToMany に紐づけ
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

            # ③ 保存できたら一覧ページへ戻る
            return redirect("ssk:post_list")

    else:
        form = PostForm()

    return render(request, "teams/ssk/post_form.html", {"form": form})

def post_detail(request, pk):
    """
    Show a single post (イベントの本文を表示).
    """
    post = get_object_or_404(Post.objects.prefetch_related("tags"), pk=pk)
    return render(request, "teams/ssk/post_detail.html", {"post": post})

def post_edit(request, pk):
    """
    Edit an existing post.
    """
    post = get_object_or_404(Post, pk=pk)

    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            # update core fields
            post.title = form.cleaned_data["title"]
            post.date = form.cleaned_data["date"]
            post.body = form.cleaned_data["body"]
            post.save()

            # parse tags_text and replace post.tags
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
        # prefill tags_text from current tags (show as "#name #name")
        tags_initial = " ".join("#" + t.name for t in post.tags.all())
        form = PostForm(instance=post, initial={"tags_text": tags_initial})

    return render(request, "teams/ssk/post_form.html", {"form": form, "post": post})


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
