# Apple Shortcuts Documentation

Generated on {{ timestamp }}

## Overview

Total Actions: {{ total_actions }}
Total Parameter Variations: {{ total_variations }}

## Actions

{% for action in actions %}

### {{ action.name }}

**Identifier**: `{{ action.identifier }}`
**Versions**: {{ action.versions|join(', ') }}

#### Parameters

{% for param in action.parameters %}

- {{ param }}
{% endfor %}

{% if action.examples %}

#### Examples

```json
{{ action.examples }}
```

{% endif %}
{% endfor %}
