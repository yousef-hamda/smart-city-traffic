{{/* Common labels applied to every object. */}}
{{- define "smart-city.labels" -}}
app.kubernetes.io/part-of: smart-city-traffic
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end -}}

{{/* Per-service selector labels. Call with (dict "name" $name). */}}
{{- define "smart-city.selectorLabels" -}}
app.kubernetes.io/name: {{ .name }}
{{- end -}}

{{/* Full image reference for a service. Call with (dict "ctx" $ "name" $name). */}}
{{- define "smart-city.image" -}}
{{- $g := .ctx.Values.global -}}
{{ $g.imageRegistry }}/{{ .name }}:{{ $g.imageTag }}
{{- end -}}
