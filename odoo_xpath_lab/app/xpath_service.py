from copy import deepcopy
from typing import Any

from lxml import etree

from app.xml_validator import parse_xml


SUPPORTED_POSITIONS = {
    "inside",
    "before",
    "after",
    "replace",
    "attributes",
}


def serialize_xml(element: etree._Element) -> str:
    return etree.tostring(
        element,
        pretty_print=True,
        encoding="unicode",
    )


def parse_fragment(fragment: str) -> list[etree._Element]:
    """Parse one or more XML nodes by wrapping them in a temporary root."""
    if not fragment or not fragment.strip():
        return []

    wrapper = f"<wrapper>{fragment}</wrapper>"
    root = parse_xml(wrapper)
    return [deepcopy(child) for child in root]


def extract_attribute_changes(fragment: str) -> dict[str, str | None]:
    """Read Odoo-style <attribute name="...">value</attribute> nodes."""
    nodes = parse_fragment(fragment)
    changes: dict[str, str | None] = {}

    for node in nodes:
        if node.tag != "attribute":
            raise ValueError(
                'For position="attributes", inherited XML must contain only '
                '<attribute name="...">value</attribute> nodes.'
            )

        name = node.get("name")
        if not name:
            raise ValueError("Every <attribute> node requires a name attribute.")

        remove_flag = node.get("remove")
        if remove_flag in {"1", "true", "True"}:
            changes[name] = None
            continue

        value = "".join(node.itertext()).strip()
        changes[name] = value

    if not changes:
        raise ValueError(
            'At least one <attribute name="...">value</attribute> node is required.'
        )

    return changes


def generate_warnings(
    xpath_expression: str,
    match_count: int,
) -> list[str]:
    warnings: list[str] = []

    if "@string=" in xpath_expression:
        warnings.append(
            "Using @string is fragile because labels can change with translations "
            "or other inherited views. Prefer @name where possible."
        )

    if "@class=" in xpath_expression and "contains(" not in xpath_expression:
        warnings.append(
            "Exact class matching may fail when an element has multiple CSS classes. "
            "Prefer contains(@class, 'class_name')."
        )

    if xpath_expression.startswith("/") and not xpath_expression.startswith("//"):
        warnings.append(
            "Absolute XPath expressions are often fragile in Odoo. "
            "A relative expression beginning with // is usually safer."
        )

    if match_count > 1:
        warnings.append(
            f"The XPath matched {match_count} elements. "
            "The operation will be applied to every matched element."
        )

    return warnings


def apply_position(
    target: etree._Element,
    position: str,
    new_nodes: list[etree._Element],
    attribute_changes: dict[str, str | None] | None = None,
) -> None:
    if position == "inside":
        if not new_nodes:
            raise ValueError('New XML is required for position="inside".')
        for node in new_nodes:
            target.append(deepcopy(node))
        return

    if position in {"before", "after", "replace"}:
        parent = target.getparent()
        if parent is None:
            raise ValueError(
                f'Cannot use position="{position}" on the root XML element.'
            )

        if position == "before":
            insert_index = parent.index(target)
            for offset, node in enumerate(new_nodes):
                parent.insert(insert_index + offset, deepcopy(node))
            return

        if position == "after":
            insert_index = parent.index(target) + 1
            for offset, node in enumerate(new_nodes):
                parent.insert(insert_index + offset, deepcopy(node))
            return

        if position == "replace":
            insert_index = parent.index(target)
            for offset, node in enumerate(new_nodes):
                parent.insert(insert_index + offset, deepcopy(node))
            parent.remove(target)
            return

    if position == "attributes":
        if not attribute_changes:
            raise ValueError("Attribute changes are required.")

        for name, value in attribute_changes.items():
            if value is None:
                target.attrib.pop(name, None)
            else:
                target.set(name, value)
        return

    raise ValueError(f"Unsupported position: {position}")


def apply_xpath(
    base_xml: str,
    xpath_expression: str,
    position: str,
    inherited_xml: str = "",
) -> dict[str, Any]:
    if position not in SUPPORTED_POSITIONS:
        return {
            "success": False,
            "error_type": "unsupported_position",
            "error": (
                f'Unsupported position "{position}". '
                f"Supported positions: {', '.join(sorted(SUPPORTED_POSITIONS))}."
            ),
        }

    try:
        root = parse_xml(base_xml)
    except ValueError as error:
        return {
            "success": False,
            "error_type": "xml_syntax_error",
            "error": str(error),
        }

    try:
        matches = root.xpath(xpath_expression)
    except etree.XPathError as error:
        return {
            "success": False,
            "error_type": "xpath_error",
            "error": f"Invalid XPath expression: {error}",
        }

    if not isinstance(matches, list):
        return {
            "success": False,
            "error_type": "invalid_match_type",
            "error": (
                "The XPath returned a number, string, or boolean value. "
                "Use an XPath that returns XML elements."
            ),
        }

    if not matches:
        return {
            "success": False,
            "error_type": "no_match",
            "error": "The XPath expression did not match any XML element.",
            "match_count": 0,
            "warnings": generate_warnings(xpath_expression, 0),
        }

    if any(not isinstance(item, etree._Element) for item in matches):
        return {
            "success": False,
            "error_type": "invalid_match_type",
            "error": (
                "The XPath returned text, attributes, numbers, or boolean values. "
                "Use an XPath that returns XML elements."
            ),
        }

    matched_xml = [serialize_xml(match) for match in matches]
    warnings = generate_warnings(xpath_expression, len(matches))

    try:
        attribute_changes = None
        new_nodes: list[etree._Element] = []

        if position == "attributes":
            attribute_changes = extract_attribute_changes(inherited_xml)
        else:
            new_nodes = parse_fragment(inherited_xml)
            if not new_nodes:
                raise ValueError(
                    f'New XML is required for position="{position}".'
                )

        # Copy the list because replacing nodes mutates the tree.
        for target in list(matches):
            apply_position(
                target=target,
                position=position,
                new_nodes=new_nodes,
                attribute_changes=attribute_changes,
            )

    except ValueError as error:
        return {
            "success": False,
            "error_type": "application_error",
            "error": str(error),
            "match_count": len(matches),
            "matched_elements": matched_xml,
            "warnings": warnings,
        }

    return {
        "success": True,
        "match_count": len(matches),
        "matched_elements": matched_xml,
        "final_xml": serialize_xml(root),
        "warnings": warnings,
    }
