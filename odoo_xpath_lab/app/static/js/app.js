const baseXml = document.getElementById("baseXml");
const xpathExpression = document.getElementById("xpathExpression");
const position = document.getElementById("position");
const inheritedXml = document.getElementById("inheritedXml");
const testButton = document.getElementById("testButton");
const exampleButton = document.getElementById("exampleButton");
const clearButton = document.getElementById("clearButton");
const copyButton = document.getElementById("copyButton");
const statusBox = document.getElementById("statusBox");
const matchedElements = document.getElementById("matchedElements");
const finalXml = document.getElementById("finalXml");


function loadExample() {
    baseXml.value = `<form string="Sale Order">
    <header>
        <button name="action_confirm" string="Confirm" type="object"/>
    </header>
    <sheet>
        <group>
            <field name="partner_id"/>
            <field name="date_order"/>
        </group>
    </sheet>
</form>`;

    xpathExpression.value = `//field[@name='partner_id']`;
    position.value = "after";
    inheritedXml.value = `<field name="customer_reference"/>`;
    statusBox.innerHTML = "";
    matchedElements.textContent = "No result yet.";
    finalXml.textContent = "No result yet.";
}


function clearForm() {
    baseXml.value = "";
    xpathExpression.value = "";
    position.value = "after";
    inheritedXml.value = "";
    statusBox.innerHTML = "";
    matchedElements.textContent = "No result yet.";
    finalXml.textContent = "No result yet.";
}


function renderWarnings(warnings) {
    if (!warnings || warnings.length === 0) {
        return "";
    }

    const items = warnings
        .map((warning) => `<li>${escapeHtml(warning)}</li>`)
        .join("");

    return `
        <div class="alert alert-warning mt-2 mb-0">
            <strong>Warnings</strong>
            <ul class="mb-0">${items}</ul>
        </div>
    `;
}


function renderResult(result) {
    if (!result.success) {
        statusBox.innerHTML = `
            <div class="alert alert-danger">
                <strong>${escapeHtml(result.error_type || "error")}</strong><br>
                ${escapeHtml(result.error || "Unknown error")}
                ${renderWarnings(result.warnings)}
            </div>
        `;

        matchedElements.textContent = (result.matched_elements || []).join("\n\n");
        finalXml.textContent = "No final XML generated.";
        return;
    }

    statusBox.innerHTML = `
        <div class="alert alert-success">
            XML is valid. XPath matched
            <strong>${result.match_count}</strong> element(s).
            ${renderWarnings(result.warnings)}
        </div>
    `;

    matchedElements.textContent = result.matched_elements.join("\n\n");
    finalXml.textContent = result.final_xml;
}


async function testXPath() {
    const payload = {
        base_xml: baseXml.value,
        xpath_expression: xpathExpression.value,
        position: position.value,
        inherited_xml: inheritedXml.value,
    };

    testButton.disabled = true;
    testButton.textContent = "Testing...";

    try {
        const response = await fetch("/api/test-xpath", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        });

        const result = await response.json();

        if (!response.ok) {
            const message = result.detail
                ? JSON.stringify(result.detail)
                : "Request failed.";
            throw new Error(message);
        }

        renderResult(result);
    } catch (error) {
        statusBox.innerHTML = `
            <div class="alert alert-danger">
                ${escapeHtml(error.message)}
            </div>
        `;
    } finally {
        testButton.disabled = false;
        testButton.textContent = "Test XPath";
    }
}


function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


async function copyFinalXml() {
    if (!finalXml.textContent || finalXml.textContent === "No result yet.") {
        return;
    }

    await navigator.clipboard.writeText(finalXml.textContent);
    copyButton.textContent = "Copied";
    setTimeout(() => {
        copyButton.textContent = "Copy";
    }, 1200);
}


testButton.addEventListener("click", testXPath);
exampleButton.addEventListener("click", loadExample);
clearButton.addEventListener("click", clearForm);
copyButton.addEventListener("click", copyFinalXml);

loadExample();
