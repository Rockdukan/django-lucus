"""
Optional ``TabularInline`` subclasses and mix-ins for Lucus admin.

Sortable tabular inlines (Grappelli-style)
------------------------------------------
Requires a numeric ordering field on the child model (typically
``PositiveIntegerField`` / ``PositiveSmallIntegerField``, nullable). Declare
``ordering = ["position"]`` (or your field name) on the child ``Meta``.

Example::

    class ItemInline(LucusSortableTabularInline):
        model = Item
        sortable_field_name = "position"
        sortable_excludes = ("is_active",)  # fields with defaults that are “non-empty”

Placeholder inlines (between fieldsets)
---------------------------------------
In the parent ``ModelAdmin`` ``fieldsets``, add a fieldset with ``fields: ()``
and ``classes`` containing ``\"placeholder\"`` plus the inline group id (the
``id`` on the inline wrapper div — exactly ``<formset.prefix>-group``, e.g.
``items_set-group``)::

    fieldsets = (
        (None, {\"fields\": (\"title\",)}),
        (\"Items\", {\"classes\": (\"placeholder\", \"items_set-group\"), \"fields\": ()}),
        (\"Meta\", {\"fields\": (\"slug\",)}),
    )
"""

from __future__ import annotations

from django import forms
from django.contrib import admin


class LucusSortableTabularInlineMixin:
    """
    Drag-and-drop reordering for tabular inlines + hidden ordering field widget.

    Set ``sortable_field_name`` to your model’s ordering field name.
    ``sortable_excludes`` lists child field names that have default values but
    should not count as “this row is filled” when reindexing positions.
    """

    sortable_field_name: str = "position"
    sortable_excludes: tuple[str, ...] = ()

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == self.sortable_field_name:
            kwargs.setdefault("widget", forms.HiddenInput)
            kwargs.setdefault("required", False)
        return super().formfield_for_dbfield(db_field, request, **kwargs)


class LucusSortableTabularInline(LucusSortableTabularInlineMixin, admin.TabularInline):
    """Concrete tabular inline with :class:`LucusSortableTabularInlineMixin` applied."""
