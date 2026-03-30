{{/*
Expand the name of the chart.
*/}}
{{- define "pdfGenerator.name" -}}
{{- printf "pdf-generator" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "pdfGenerator.fullname" -}}
{{- $componentName := include "pdfGenerator.name" .  }}
{{- if .Values.pdfGenerator.fullnameOverride }}
{{- .Values.pdfGenerator.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $componentName | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "pdfGenerator.labels" -}}
{{ include "pdfGenerator.selectorLabels" . }}
{{- if .Values.global.tag }}
app.kubernetes.io/image-version: {{ .Values.global.tag | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/short-name: {{ include "pdfGenerator.name" . }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "pdfGenerator.selectorLabels" -}}
app.kubernetes.io/name: {{ include "pdfGenerator.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}


