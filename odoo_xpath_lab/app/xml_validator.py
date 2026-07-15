from lxml import etree


MAX_XML_SIZE = 500_000


def parse_xml(xml_content: str) -> etree._Element:
    """Safely parse XML and reject malformed or oversized input."""
    if not isinstance(xml_content, str):
        raise ValueError("XML content must be a string.")

    if len(xml_content) > MAX_XML_SIZE:
        raise ValueError(
            f"XML input is too large. Maximum allowed size is {MAX_XML_SIZE} characters."
        )

    parser = etree.XMLParser(
        remove_blank_text=True,
        recover=False,
        resolve_entities=False,
        no_network=True,
        load_dtd=False,
        huge_tree=False,
    )

    try:
        return etree.fromstring(xml_content.encode("utf-8"), parser=parser)
    except (etree.XMLSyntaxError, ValueError) as error:
        raise ValueError(f"Invalid XML: {error}") from error
