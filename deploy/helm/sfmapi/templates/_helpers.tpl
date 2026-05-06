{{/*
Common name + label helpers, mirroring Bitnami / official chart conventions.
*/}}

{{- define "sfmapi.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "sfmapi.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{- define "sfmapi.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "sfmapi.labels" -}}
helm.sh/chart: {{ include "sfmapi.chart" . }}
{{ include "sfmapi.selectorLabels" . }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- with .Values.commonLabels }}
{{ toYaml . }}
{{- end }}
{{- end -}}

{{- define "sfmapi.selectorLabels" -}}
app.kubernetes.io/name: {{ include "sfmapi.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "sfmapi.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
{{- default (include "sfmapi.fullname" .) .Values.serviceAccount.name -}}
{{- else -}}
{{- default "default" .Values.serviceAccount.name -}}
{{- end -}}
{{- end -}}

{{/*
Compute the SFMAPI_DB_URL value. Prefer the bundled Postgres subchart
when enabled; otherwise the operator must set `env.extraEnv.SFMAPI_DB_URL`.
*/}}
{{- define "sfmapi.dbUrl" -}}
{{- if .Values.postgresql.enabled -}}
postgresql+psycopg://{{ .Values.postgresql.auth.username }}:{{ .Values.postgresql.auth.password }}@{{ .Release.Name }}-postgresql:5432/{{ .Values.postgresql.auth.database }}
{{- else -}}
{{ default "" (index .Values.env.extraEnv "SFMAPI_DB_URL") }}
{{- end -}}
{{- end -}}

{{- define "sfmapi.redisUrl" -}}
{{- if .Values.redis.enabled -}}
redis://{{ .Release.Name }}-redis-master:6379/0
{{- else -}}
{{ default "" (index .Values.env.extraEnv "SFMAPI_REDIS_URL") }}
{{- end -}}
{{- end -}}

{{- define "sfmapi.image" -}}
{{- $reg := .Values.image.registry -}}
{{- $repo := .Values.image.repository -}}
{{- $tag := default .Chart.AppVersion .Values.image.tag -}}
{{- if $reg -}}
{{- printf "%s/%s:%s" $reg $repo $tag -}}
{{- else -}}
{{- printf "%s:%s" $repo $tag -}}
{{- end -}}
{{- end -}}

{{- define "sfmapi.workerImage" -}}
{{- $reg := .Values.worker.image.registry -}}
{{- $repo := .Values.worker.image.repository -}}
{{- $tag := default .Chart.AppVersion .Values.worker.image.tag -}}
{{- if $reg -}}
{{- printf "%s/%s:%s" $reg $repo $tag -}}
{{- else -}}
{{- printf "%s:%s" $repo $tag -}}
{{- end -}}
{{- end -}}

{{/*
Common environment block injected into both web and worker pods.
*/}}
{{- define "sfmapi.commonEnv" -}}
- name: SFMAPI_DB_URL
  value: {{ include "sfmapi.dbUrl" . | quote }}
- name: SFMAPI_REDIS_URL
  value: {{ include "sfmapi.redisUrl" . | quote }}
- name: SFMAPI_AUTH_MODE
  value: {{ .Values.env.authMode | quote }}
- name: SFMAPI_LOG_LEVEL
  value: {{ .Values.env.logLevel | quote }}
- name: SFMAPI_INLINE_TASKS
  value: {{ .Values.env.inlineTasks | quote }}
- name: SFMAPI_WORKSPACE_ROOT
  value: "/workspaces"
- name: SFMAPI_BLOB_ROOT
  value: "/workspaces/_blobs"
- name: SFMAPI_S3_CACHE_ROOT
  value: "/workspaces/_cache/s3"
{{- range $k, $v := .Values.env.extraEnv }}
- name: {{ $k }}
  value: {{ $v | quote }}
{{- end }}
{{- end -}}
