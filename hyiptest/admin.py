from django.contrib import admin

from hyiptest.models import Answer, BadDomain, BadSite, HtestSnapshot, Question


class BadDomainInline(admin.StackedInline):
    model = BadDomain
    extra = 1


@admin.register(BadSite)
class BadSiteAdmin(admin.ModelAdmin):
    list_display = ("name", "bad_type", "display_domains", "id", "updated_at")
    list_filter = ("updated_at", "bad_type", "name", "created_at")
    fields = ["name", "bad_type"]
    inlines = [BadDomainInline]


class AnswerInline(admin.StackedInline):
    model = Answer
    extra = 2


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "created_at")
    list_filter = ("created_at",)
    inlines = [AnswerInline]


admin.site.register(HtestSnapshot)
