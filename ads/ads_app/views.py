
from django.contrib import messages

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils.html import strip_tags
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView

from .filters import AdsFilter
from .forms import AdsForm, CommentForm
from .models import Ads, Comment, Profile
from ads import settings


class AdsList(ListView):
    model = Ads
    template_name = 'ads.html'
    context_object_name = 'ads'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = AdsFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class AdsCreate(LoginRequiredMixin, CreateView):
    form_class = AdsForm
    model = Ads
    template_name = 'ads_create.html'
    success_url = reverse_lazy('ads_list')
    permission_required = ('ads_app.add_ads',)

    def form_valid(self, form):
        form.instance.author = self.request.user  # автором станет текущий пользователь
        return super().form_valid(form)


class AdsDetail(DetailView):
    model = Ads
    template_name = 'ads_detail.html'
    context_object_name = 'ads_detail'
    queryset = Ads.objects.all()
    form = CommentForm

    def post(self, request, *args, **kwargs):
        form = CommentForm(request.POST)
        if form.is_valid():
            ads_detail = self.get_object()
            form.instance.user = request.user
            form.instance.ads = ads_detail
            comment = form.save()
            request.user.profile.comments.add(comment)

            # отправка уведомления на почту
            subject = f"Новый комментарий был добавлен к '{ads_detail.title}'"
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = ads_detail.author.email  # адрес получателя - автор объявления
            context = {
                'comment': comment,
                'ad': ads_detail,
            }
            html_message = render_to_string('new_comment_email.html', context)
            plain_message = strip_tags(html_message)
            send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)

            return redirect(reverse("ads_detail", kwargs={
                'pk': ads_detail.pk
            }))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.form
        comments = Comment.objects.filter(ads__author=self.request.user, ads=self.get_object())
        context["comments"] = comments
        return context


class CommentView(ListView):
    model = Comment
    ordering = ['-time_in']
    paginate_by = 10
    template_name = 'comment_list.html'
    context_object_name = 'comments'

    def comments(request):
        comments = Comment.objects.all()
        ads = Ads.objects.all()
        context = {'comments': comments, 'ads': ads}
        return render(request, 'comments_list.html', context)


class AdUpdate(UpdateView):
    model = Ads
    template_name = 'edit_ad.html'
    fields = ['title', 'text', 'category', 'image', 'video']
    success_url = '/ads/'


class AdDelete(DeleteView):
    model = Ads
    template_name = 'delete_ad.html'
    success_url = reverse_lazy('ads_list')


class MyResponsesView(ListView):
    model = Comment
    template_name = 'my_responses.html'
    context_object_name = 'comments'

    def get_queryset(self):
        queryset = super().get_queryset().filter(ads__author=self.request.user)
        ads_id = self.request.GET.get('ads')
        if ads_id:
            queryset = queryset.filter(ads_id=ads_id)
        return queryset


def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.ads.author == request.user:
        comment.delete()
        messages.success(request, 'Comment deleted successfully.')
    else:
        messages.error(request, 'You do not have permission to delete this comment.')
    return redirect('my_responses')


def accept_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.ads.author == request.user:
        ads = comment.ads
        ads.comments.add(comment)  # Add the comment to the announcement
        comment.is_accepted = True  # Set the comment as accepted
        comment.save()
        ads.save()

        send_mail(
            subject='Действия с вашим откликом',
            message=f'Ваш отклик "{comment.text}" к "{comment.ads.title}" был одобрен',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[comment.user.email],
        )
        messages.success(request, 'Comment accepted and added to the announcement.')
    else:
        messages.error(request, 'You do not have permission to accept this comment.')
    return redirect('my_responses')


def my_responses(request):
    user = request.user
    if request.method == 'POST':
        if 'accept_comment' in request.POST:
            comment_id = request.POST.get('accept_comment')
            comment = Comment.objects.get(pk=comment_id)
            comment.delete()  # Delete the comment from the database

        if 'delete_comment' in request.POST:
            comment_id = request.POST.get('delete_comment')
            comment = Comment.objects.get(pk=comment_id)
            comment.delete()  # Delete the comment from the database

    comments = Comment.objects.filter(ads__author=user)
    ads = Ads.objects.filter(author=user)
    return render(request, 'my_responses.html', {'comments': comments, 'ads': ads})


def profile_list(request):
    if request.user.is_authenticated:
        profiles = Profile.objects.exclude(user=request.user)
        return render(request, 'profile_list.html', {"profiles": profiles})
    else:
        messages.success(request, ("You must be logged in to view this page."))
        return redirect('home')


def profile(request, pk):
    if request.user.is_authenticated:
        profile = Profile.objects.get(user_id=pk)
        ads = Ads.objects.filter(author_id=pk)

        if request.method == "POST":
            current_user_profile = request.user.profile
            action = request.POST['follow']
            if action == "unfollow":
                current_user_profile.follows.remove(profile)
            elif action == "follow":
                current_user_profile.follows.add(profile)
            current_user_profile.save()


        return render(request, "profile.html", {"profile": profile, "ads": ads})
    else:
        messages.success(request, ("You must be logged in to view this page."))
        return redirect('home')