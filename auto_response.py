"""Builds the automatic acknowledgment message a requester gets right after submitting a ticket."""

def build_acknowledgment(ticket_id, category, priority):
    lines = [f"Your ticket #{ticket_id} has been received."]
    if priority:
        lines.append(f"Priority: {priority} (set automatically). Our staff may adjust it after review.")
    if category:
        lines.append(f"Suggested category: {category}.")
    else:
        lines.append("Our support staff will review its category.")
    lines.append("A technician will be assigned soon. You can reply here with the affected device or service, "
                 "any error message, and when the problem started.")
    lines.append("Please never share passwords or verification codes.")
    return "\n\n".join(lines)