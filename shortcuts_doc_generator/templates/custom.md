# Custom Template
Actions: {{ total_actions }}
{% for action in actions %}
- {{ action.name }}
{% endfor %}
