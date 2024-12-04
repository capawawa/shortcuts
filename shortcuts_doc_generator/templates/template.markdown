# Apple Shortcuts Documentation

Generated on {{ timestamp }}

## Overview

Total Actions: {{ total_actions }}
Total Variations: {{ total_variations }}

## Actions

{% for action in actions %}

### {{ action.name }}

- Identifier: {{ action.identifier }}
- Parameters: {{ action.parameters|join(', ') }}
{% endfor %}
