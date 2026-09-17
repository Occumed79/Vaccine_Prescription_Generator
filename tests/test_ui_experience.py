import ui_experience


def test_landing_html_contains_vial_lineup_particle_canvas_and_logo_reference():
    html = ui_experience._build_landing_html()
    assert 'id="particle-field"' in html
    assert 'class="vial-lineup"' in html
    assert html.count('class="vial-shell') >= 5
    assert 'occu-med-logo.png' in html


def test_landing_html_contains_color_matched_aura_configuration():
    html = ui_experience._build_landing_html()
    for rgb in ["174, 82, 255", "58, 255, 95", "42, 165, 255", "41, 238, 240"]:
        assert rgb in html
    assert "auraBreath" in html


def test_landing_html_respects_reduced_motion():
    html = ui_experience._build_landing_html()
    assert "prefers-reduced-motion: reduce" in html
    assert "matchMedia('(prefers-reduced-motion: reduce)')" in html
    assert "reducedMotion.matches" in html


def test_landing_has_no_pricing_agreement_artifacts():
    html = ui_experience._build_landing_html()
    assert "Pricing Agreement" not in html
    assert "price-sheet" not in html
