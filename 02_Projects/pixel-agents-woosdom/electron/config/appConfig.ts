import * as fs from 'node:fs'
import * as os from 'node:os'
import * as path from 'node:path'

interface AppConfig {
  vaultRoot?: string
}

const DEFAULT_VAULT_ROOT = path.join(os.homedir(), 'Desktop', 'Dev', 'Woosdom_Brain')

function getAppRoot(): string {
  return process.env.APP_ROOT ?? path.join(__dirname, '..', '..')
}

function readAppConfig(): AppConfig {
  const configPath = path.join(getAppRoot(), 'config', 'app-config.json')

  try {
    const raw = fs.readFileSync(configPath, 'utf-8')
    const parsed = JSON.parse(raw) as AppConfig
    return parsed ?? {}
  } catch {
    return {}
  }
}

export function getVaultRoot(): string {
  const envRoot = process.env.VAULT_ROOT?.trim()
  if (envRoot) return envRoot

  const configRoot = readAppConfig().vaultRoot?.trim()
  if (configRoot) return configRoot

  return DEFAULT_VAULT_ROOT
}
