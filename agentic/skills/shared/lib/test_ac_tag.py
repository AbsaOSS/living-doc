#!/usr/bin/env python3
"""
Tag-grammar tests for ac_tag.py — the `@AC:` scenario tag as the canon defines it.

Covers the AC-variants rule from living-doc-bdd-schemas.md#ac-variants, which the tag
grammar has to carry: a tag takes **at most one** `/<param>:<value>` segment, and `<param>`
is one lowercase kebab-case name. A tag with two parameters is MALFORMED_AC, so it must fail
the match rather than being silently truncated to the first segment — the behaviour before
this rule landed, which let `@AC:US-1-01/aspect:a/field:b` read as a valid single-value tag.
"""
__test__ = False  # pytest: ignore this helper script

import sys

from ac_tag import AC_ID_PATTERN, VARIANT_NAME, match_ac_tag


def test_bare_tag_accepted():
    """A bare tag covers the whole AC — every value of one that declares variants."""
    assert match_ac_tag("@AC:US-1-01")
    assert match_ac_tag("@AC:FUNC-001-02")
    print("✓ A bare @AC: tag is accepted")


def test_one_variant_parameter_accepted():
    """One `/<param>:<value>`: `aspect` for an `- Aspect:` declaration, or the AC's keyword."""
    assert match_ac_tag("@AC:US-1-01/aspect:username-input")
    assert match_ac_tag("@AC:FUNC-001-02/payment-method:card")
    print("✓ A tag with one variant parameter is accepted")


def test_two_variant_parameters_rejected():
    """A scenario covers one value, so one scenario is tagged per value. Two parameters on one
    tag is MALFORMED_AC — and must not match, or the second segment is quietly ignored."""
    assert match_ac_tag("@AC:US-1-01/aspect:a/field:b") is None
    assert match_ac_tag("@AC:US-1-01/field:a/role:b") is None
    print("✓ A tag with two variant parameters is rejected")


def test_uppercase_parameter_name_rejected():
    """The name is written identically in the AC text, the declaration and the tag, and the
    canon spells it lowercase kebab-case. `Aspect:` in a tag is not that spelling."""
    assert match_ac_tag("@AC:US-1-01/Aspect:X") is None
    assert match_ac_tag("@AC:US-1-01/Payment-Method:card") is None
    print("✓ An upper-case variant parameter name is rejected")


def test_entity_id_case_insensitive():
    """The id itself stays case-insensitive, as it was before the variant rule."""
    assert match_ac_tag("@AC:us-1-01")
    assert match_ac_tag("@AC:func-001-02")
    print("✓ The entity id is still matched case-insensitively")


def test_trailing_digit_not_swallowed():
    """`@AC:US-1-011` is not `@AC:US-1-01` with a stray digit — the suffix is exactly two."""
    assert match_ac_tag("@AC:US-1-011") is None
    print("✓ A three-digit AC suffix is rejected")


def test_variant_name_pattern_is_kebab_case():
    """VARIANT_NAME is the one spelling shared by the text, the bullet and the tag."""
    import re

    name = re.compile(VARIANT_NAME)
    for ok in ("aspect", "channel", "payment-method", "field2"):
        assert name.fullmatch(ok), ok
    for bad in ("Channel", "payment_method", "-channel", "channel-", "2field"):
        assert not name.fullmatch(bad), bad
    print("✓ VARIANT_NAME accepts only lowercase kebab-case names")


def test_ac_id_pattern_unaffected():
    """AC_ID_PATTERN validates an AC's own `id` field and takes no tag parameters."""
    assert AC_ID_PATTERN.match("AC:US-1-01")
    assert AC_ID_PATTERN.match("AC:FUNC-001-02")
    assert not AC_ID_PATTERN.match("AC:US-1-01/aspect:a")
    assert not AC_ID_PATTERN.match("@AC:US-1-01")
    print("✓ AC_ID_PATTERN still matches the bare id form only")


if __name__ == "__main__":
    try:
        test_bare_tag_accepted()
        test_one_variant_parameter_accepted()
        test_two_variant_parameters_rejected()
        test_uppercase_parameter_name_rejected()
        test_entity_id_case_insensitive()
        test_trailing_digit_not_swallowed()
        test_variant_name_pattern_is_kebab_case()
        test_ac_id_pattern_unaffected()
        print("\n✓ All tests passed!")
    except AssertionError as e:
        print(f"✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
