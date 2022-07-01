from flask import Blueprint, flash, render_template, request, session, url_for, redirect, jsonify
from flask_login import login_required, current_user
from .models import Post, User, Comment, Like
from .__init__ import db

views = Blueprint("views", __name__)


@views.route("/")
@views.route("/home")
def home():
    return render_template("home.html", user=current_user)


@views.route("/stories")

def stories():
    posts = Post.query.all()
    return render_template("all_rubrics.html", user=current_user, posts=posts)


@views.route("/create_post", methods=["GET", "POST"])
@login_required
def create_post():
    if request.method == 'POST':
        rubric = request.form.get('selection')
        text = request.form.get('text')
        if not text:
            flash('Поле не должно быть пустым!', category='error')
        else:
            post = Post(text=text, author=current_user.id, rubric=rubric)
            db.session.add(post)
            db.session.commit()
            flash('История опубликована!', category='success')
            return redirect(url_for('views.stories'))
    
    return render_template('create_post.html', user=current_user)


@views.route("/delete_post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()
    
    if not post:
        flash("Публикация не существует", category='error')
    elif current_user.id != post.author:
        flash('У Вас нет прав для удаления истории', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Публикации больше нет!', category='success')
        
    return redirect(url_for('views.stories'))


@views.route("/posts/<username>")
@login_required
def posts(username):
    user = User.query.filter_by(username=username).first()
    
    if not user:
        flash('Нет пользователя с таким именем')
        return redirect(url_for('views.home'))
    
    posts = user.posts
    
    return render_template("user_posts.html", user=current_user, posts=posts, username=username)


@views.route("/exact_rubric/<rubric>")
#@login_required
def exact_rubric(rubric):
    if rubric == 'anime':
        posts = Post.query.filter(Post.rubric == 'anime').all()
        rubric_value = 'anime'
    elif rubric == 'cyberpunk':
        posts = Post.query.filter(Post.rubric == 'cyberpunk').all()
        rubric_value = 'cyberpunk'
    elif rubric == 'history':
        posts = Post.query.filter(Post.rubric == 'history').all()
        rubric_value = 'history'
    elif rubric == 'anecdote':
        posts = Post.query.filter(Post.rubric == 'anecdote').all()
        rubric_value = 'anecdote'
    elif rubric == 'romantic':
        posts = Post.query.filter(Post.rubric == 'romantic').all()
        rubric_value = 'romantic'
    elif rubric == 'superhero':
        posts = Post.query.filter(Post.rubric == 'superhero').all()
        rubric_value = 'superhero'
    elif rubric == 'fantasy':
        posts = Post.query.filter(Post.rubric == 'fantasy').all()
        rubric_value = 'fantasy'
    else:
        flash('Упс, что-то пошло не так...', category='error')
    
    session['my_var'] = rubric_value
    amount = len(posts)
    if amount == 0:
       flash('На эту тематику пока что нет историй, но вы можете это исправить!', category='success')    
    
    return render_template("exact_rubric_posts.html", user=current_user, posts=posts, rubrica=rubric_value)


@views.route("/create_comment/<post_id>", methods=['POST'])
def create_comment(post_id):
    text = request.form.get('text')
    
    if not text:
        flash('Комментарий не может быть пустым!', category='error')
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
            flash('Вы добавили комментарий!', category='success')
        else:
            flash('Публикация не существует', category='error')
    
    my_var = session.get('my_var', None)   
    return redirect(url_for('views.exact_rubric', rubric=my_var))
    
    
@views.route("/delete_comment/<comment_id>")
#@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()
    print(comment)

    if not comment:
        flash("Комментарий не существует", category='error')
    elif current_user.id != comment.author or current_user.id != comment.post.author:
        flash('You do not have permission to delete this post.', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()
        flash('Вы удалили комментарий!', category='success')

    #my_var = session.get('my_var', None)
    return redirect(url_for('views.stories'))


@views.route("/like_post/<post_id>", methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(author=current_user.id, post_id=post_id).first()
    
    if not post:
        return jsonify({'error': 'Публикация не существует'}, 400)
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()
        
    return jsonify({"likes": len(post.likes), "liked": current_user.id in map(lambda x: x.author, post.likes)})
