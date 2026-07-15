from app.xpath_service import apply_xpath


BASE_XML = """
<form string="Sale Order">
    <header>
        <button name="action_confirm" string="Confirm" type="object"/>
    </header>
    <sheet>
        <group>
            <field name="partner_id"/>
            <field name="date_order"/>
        </group>
    </sheet>
</form>
"""


def test_after_position():
    result = apply_xpath(
        base_xml=BASE_XML,
        xpath_expression="//field[@name='partner_id']",
        position="after",
        inherited_xml='<field name="customer_reference"/>',
    )

    assert result["success"] is True
    assert result["match_count"] == 1
    assert 'name="customer_reference"' in result["final_xml"]


def test_inside_position():
    result = apply_xpath(
        base_xml=BASE_XML,
        xpath_expression="//group",
        position="inside",
        inherited_xml='<field name="note"/>',
    )

    assert result["success"] is True
    assert 'name="note"' in result["final_xml"]


def test_before_position():
    result = apply_xpath(
        base_xml=BASE_XML,
        xpath_expression="//field[@name='date_order']",
        position="before",
        inherited_xml='<field name="client_order_ref"/>',
    )

    assert result["success"] is True
    assert result["final_xml"].index("client_order_ref") < result["final_xml"].index("date_order")


def test_replace_position():
    result = apply_xpath(
        base_xml=BASE_XML,
        xpath_expression="//button[@name='action_confirm']",
        position="replace",
        inherited_xml=(
            '<button name="action_custom_confirm" '
            'string="Custom Confirm" type="object"/>'
        ),
    )

    assert result["success"] is True
    assert "action_custom_confirm" in result["final_xml"]
    assert 'name="action_confirm"' not in result["final_xml"]


def test_attributes_position():
    result = apply_xpath(
        base_xml=BASE_XML,
        xpath_expression="//field[@name='partner_id']",
        position="attributes",
        inherited_xml=(
            '<attribute name="string">Customer</attribute>'
            '<attribute name="required">1</attribute>'
        ),
    )

    assert result["success"] is True
    assert 'string="Customer"' in result["final_xml"]
    assert 'required="1"' in result["final_xml"]


def test_no_match():
    result = apply_xpath(
        base_xml=BASE_XML,
        xpath_expression="//field[@name='missing_field']",
        position="after",
        inherited_xml='<field name="test"/>',
    )

    assert result["success"] is False
    assert result["error_type"] == "no_match"


def test_invalid_xml():
    result = apply_xpath(
        base_xml="<form><sheet></form>",
        xpath_expression="//sheet",
        position="inside",
        inherited_xml="<group/>",
    )

    assert result["success"] is False
    assert result["error_type"] == "xml_syntax_error"


def test_invalid_xpath():
    result = apply_xpath(
        base_xml=BASE_XML,
        xpath_expression="//field[@name='partner_id'",
        position="after",
        inherited_xml="<field name='x'/>",
    )

    assert result["success"] is False
    assert result["error_type"] == "xpath_error"


def test_scalar_xpath_is_rejected():
    result = apply_xpath(
        base_xml=BASE_XML,
        xpath_expression="count(//field)",
        position="inside",
        inherited_xml="<field name='x'/>",
    )

    assert result["success"] is False
    assert result["error_type"] == "invalid_match_type"
