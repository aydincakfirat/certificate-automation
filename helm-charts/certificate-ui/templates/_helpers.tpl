{{/* Helper for chart fullname */}}
{{- define "certificate-ui.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/* Helper for chart name */}}
{{- define "certificate-ui.name" -}}
{{- default .Chart.Name .Values.nameOverride }}
{{- end }}
