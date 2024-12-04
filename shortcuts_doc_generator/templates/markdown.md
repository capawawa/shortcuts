# Apple Shortcuts Documentation

Generated on {{ timestamp }}

## Overview

Total Actions: {{ total_actions }}
Total Variations: {{ total_variations }}

## Action Details

{% for action in actions %}

### {{ action.name }} (`{{ action.identifier }}`)

#### Parameters

{% if action.parameters %}
{% for param in action.parameters %}

- {{ param }}
{% endfor %}
{% else %}
- No parameters
{% endif %}

#### Examples

{% if action.examples %}
{% for example in action.examples %}

- {{ example }}
{% endfor %}
{% else %}
- No examples available
{% endif %}

{% endfor %}

## Analysis Results

### Action Flow Analysis

{{ analysis.action_flows|tojson(indent=2) }}

### Pattern Analysis

{{ analysis.common_patterns|tojson(indent=2) }}

### Usage Statistics

{{ analysis.usage_stats|tojson(indent=2) }}
