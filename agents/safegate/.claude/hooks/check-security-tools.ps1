# SafeGate - verifica ferramentas de scan no inicio da sessao (hook SessionStart)
# Saida: JSON com aviso ao usuario + contexto para o Claude oferecer a instalacao.
$tools = [ordered]@{
    'semgrep'  = 'pip install semgrep'
    'gitleaks' = 'winget install Gitleaks.Gitleaks'
    'trivy'    = 'winget install AquaSecurity.Trivy'
}
$missing = @($tools.Keys | Where-Object { -not (Get-Command $_ -ErrorAction SilentlyContinue) })
if ($missing.Count -gt 0) {
    $hints = ($missing | ForEach-Object { "$_ -> $($tools[$_])" }) -join ' | '
    $out = @{
        systemMessage      = "SafeGate: ferramentas de scan faltando: $($missing -join ', '). Instale: $hints"
        hookSpecificOutput = @{
            hookEventName     = 'SessionStart'
            additionalContext = "[SafeGate] Ferramentas de seguranca ausentes neste ambiente: $($missing -join ', '). No primeiro momento oportuno, ofereca ao usuario instala-las ($hints). Sem elas, os scans automatizados (SAST, segredos, dependencias) dos agentes de auditoria ficam indisponiveis."
        }
    }
    $out | ConvertTo-Json -Compress -Depth 4
}
exit 0
