"""Script de inicialização rápida plug-and-play para o Workout API Async Pro."""

import sys

import uvicorn

from src.configs.settings import settings


def print_startup_banner() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    base_url = f"http://{settings.HOST}:{settings.PORT}"
    cyan = "\033[96m"
    green = "\033[92m"
    magenta = "\033[95m"
    yellow = "\033[93m"
    bold = "\033[1m"
    reset = "\033[0m"

    print(
        f"""
{cyan}{bold}========================================================================
   ⚡ WORKOUT API ASYNC PRO  //  HIGH-CONCURRENCY CROSSFIT ENGINE ⚡
========================================================================{reset}
  {bold}Versão:{reset}        {settings.APP_VERSION} ({settings.APP_ENV})
  {bold}Banco Ativo:{reset}   {yellow}{settings.database_backend}{reset}
  {bold}Auto-Seed:{reset}     {"Ativado (dados de exemplo prontos no /docs)" if settings.AUTO_SEED else "Desativado"}

  {magenta}{bold}Links Diretos:{reset}
    {green}➜ Swagger UI:{reset}    {base_url}/docs
    {green}➜ ReDoc:{reset}         {base_url}/redoc
    {green}➜ Health Check:{reset}  {base_url}/health
    {green}➜ Atletas API:{reset}   {base_url}/atletas/?limit=10&offset=0
{cyan}{bold}========================================================================{reset}
"""
    )


if __name__ == "__main__":
    print_startup_banner()
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
