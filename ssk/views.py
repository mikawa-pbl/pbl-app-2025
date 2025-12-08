# ssk/views.py
from django.shortcuts import render, redirect
from .models import Post, Tag
from .forms import PostForm

def post_list(request):
    posts = Post.objects.prefetch_related("tags").order_by("date")
    return render(request, "teams/ssk/post_list.html", {
        "posts": posts,
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
