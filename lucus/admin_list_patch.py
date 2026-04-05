"""
Lucus: mark changelist boolean columns so CSS can center header + cells reliably.

Django renders thead .text a/span as display:block (lucus-admin.css); text-align on
<th> alone does not center the label. Boolean <td> may wrap the icon in <a>.
"""

from __future__ import annotations

import re
from typing import Any, Iterator

from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.utils.safestring import SafeString, mark_safe

_BOOL_SVG = re.compile(r"icon-(yes|no|unknown)\.svg")


def lucus_column_is_boolean(cl: Any, field_name: Any, field_index: int) -> bool:
    if field_name == "action_checkbox":
        return False

    from django.contrib.admin.templatetags.admin_list import _coerce_field_name
    from django.contrib.admin.utils import label_for_field

    _text, attr = label_for_field(
        field_name, cl.model, model_admin=cl.model_admin, return_attr=True
    )
    coerced = _coerce_field_name(field_name, field_index)
    try:
        f = cl.lookup_opts.get_field(coerced)
    except FieldDoesNotExist:
        f = None

    if f is not None:
        return isinstance(f, models.BooleanField)

    if attr is None:
        return False
    boolean = getattr(attr, "boolean", False)
    if isinstance(attr, property) and hasattr(attr, "fget"):
        boolean = getattr(attr.fget, "boolean", False)
    return bool(boolean)


def _inject_boolean_class_attrib(class_attrib: Any) -> SafeString:
    s = str(class_attrib) if class_attrib else ""
    if "lucus-admin-boolean" in s:
        return SafeString(s)
    if 'class="' in s:
        return SafeString(s.replace('class="', 'class="lucus-admin-boolean ', 1))
    return SafeString(' class="lucus-admin-boolean"')


def patched_result_headers(cl: Any) -> Iterator[dict[str, Any]]:
    from django.contrib.admin.templatetags import admin_list

    for i, header in enumerate(admin_list._lucus_orig_result_headers(cl)):
        field_name = cl.list_display[i]
        if lucus_column_is_boolean(cl, field_name, i):
            header = {
                **header,
                "class_attrib": _inject_boolean_class_attrib(header.get("class_attrib")),
            }
        yield header


def patched_items_for_result(cl: Any, result: Any, form: Any):
    from django.contrib.admin.templatetags import admin_list

    for chunk in admin_list._lucus_orig_items_for_result(cl, result, form):
        s = str(chunk)
        if not _BOOL_SVG.search(s):
            yield chunk
            continue
        s2 = re.sub(
            r"<(td|th)(\s+class=\")([^\"]*)\"",
            lambda m: (
                f'<{m.group(1)}{m.group(2)}lucus-admin-boolean {m.group(3)}"'
                if "lucus-admin-boolean" not in m.group(3)
                else m.group(0)
            ),
            s,
            count=1,
        )
        yield mark_safe(s2) if s2 != s else chunk


def apply_admin_list_boolean_patch() -> None:
    from django.contrib.admin.templatetags import admin_list

    if getattr(admin_list, "_lucus_boolean_column_patch_applied", False):
        return
    admin_list._lucus_orig_result_headers = admin_list.result_headers
    admin_list._lucus_orig_items_for_result = admin_list.items_for_result
    admin_list.result_headers = patched_result_headers
    admin_list.items_for_result = patched_items_for_result
    admin_list._lucus_boolean_column_patch_applied = True
