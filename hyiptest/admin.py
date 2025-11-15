from django.contrib import admin

from hyiptest.models import Answer, BadDomain, BadSite, Question, TestProgress


# Register your models here.
class AnswerInline(admin.StackedInline):
    model = Answer
    extra = 2


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "created")
    list_filter = ("created",)
    inlines = [AnswerInline]


class BadDomainInline(admin.StackedInline):
    model = BadDomain
    extra = 1


@admin.register(BadSite)
class BadSiteAdmin(admin.ModelAdmin):
    list_display = ("name", "bad_type", "display_domains", "id", "updated")
    list_filter = ("updated", "bad_type", "name", "created")
    fields = ["name", "bad_type"]
    inlines = [BadDomainInline]


admin.site.register(TestProgress)
