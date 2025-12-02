"""This module is the web application's interface to the agent application."""

import apps.agent.orchestrator as agent


def send_to_agent(filename: str, content: str) -> str:
    """
    Send the contents of the grocery list file to the agent
    and return the agent's response.
    """
    response = agent.main(filename, format_content(content))
    return transform_response(response)


def format_content(content: str) -> str:
    """Format the file contents before sending them to the agent."""
    formatted = "\n" + content.strip().replace("\r", "")
    phrases = formatted.split("\n")
    formatted = "<li/>".join(phrases)
    return formatted


def transform_response(
    response: dict[str, list[dict[str, str | list[dict[str, str | int | float]]]]],
) -> str:
    """Transform the agent's response into HTML."""
    recommendations_html = ""
    for product in response["recommendations"]:
        product_html = ""
        header = f"<h4>For your requirement `{product['query']}`...</h4>"
        for suggestion in product["suggestions"]:
            product_html += f"<p>{transform_suggestion(suggestion)}</p>"
        product_html = header + product_html

        recommendations_html += f"{product_html}"
    return recommendations_html


def transform_suggestion(suggestion: dict[str, str | int | float]) -> str:
    """Convert the suggestion to HTML."""
    conf = suggestion["confidence"]
    desc = suggestion["description"]
    qty = suggestion["quantity"]
    sku = suggestion["sku"]
    pr = suggestion["unit_price"]

    if conf >= 70:
        message = '<font color="green">Highly recommended!</font><br />'
    elif conf >= 40:
        message = '<font color="orange">Recommended</font><br />'
    else:
        message = '<font color="red">You may also like...</font><br />'

    checkbox = f'<input type="checkbox" id={sku} value={sku} name="sku" />'
    label = f"<label for={sku}>{create_dropdown(sku, qty)} {desc} (at ${pr} per unit)</label>"
    suggestion_html = message + checkbox + label
    return suggestion_html


def create_dropdown(sku: int, default: int) -> str:
    """Create an HTML dropdown list."""
    dropdown_html = f'<select name="qty_{sku}">'
    dropdown_options = []
    for i in range(1, 11):
        choice = f"<option value={i}>{i}</option>"
        if i == default:
            choice = choice.replace(f"{i}>", f"{i} selected>")
        dropdown_options.append(choice)

    return dropdown_html + "".join(dropdown_options) + "</select>"
