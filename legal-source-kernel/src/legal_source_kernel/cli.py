"""CLI — Typer-powered command-line interface for legal-source-kernel."""

from __future__ import annotations
import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich import box
from rich.panel import Panel
from rich.syntax import Syntax

from .config import get_db_path
from .db import init_db, get_db
from .exceptions import DuplicateSourceError
from . import tool_contracts as tc

app = typer.Typer(
    name="legal-kernel",
    help="Legal Source Kernel — fuentes jurídicas locales, verificables y citables.",
    no_args_is_help=True,
)
console = Console()
err_console = Console(stderr=True, style="bold red")


def _db() -> Path:
    return get_db_path()


# ---------------------------------------------------------------------------
# init
# ---------------------------------------------------------------------------

@app.command()
def init():
    """Inicializa la base de datos local del kernel."""
    db_path = _db()
    if db_path.exists():
        console.print(f"[yellow]Base de datos ya existe:[/yellow] {db_path}")
    else:
        init_db(db_path)
        console.print(f"[green]Base de datos creada:[/green] {db_path}")
    console.print("[dim]Usa 'legal-kernel ingest' para cargar fuentes.[/dim]")


# ---------------------------------------------------------------------------
# ingest
# ---------------------------------------------------------------------------

@app.command()
def ingest(
    file: Path = typer.Argument(..., help="Archivo a ingestar (.md, .txt, .pdf)"),
    metadata: Optional[Path] = typer.Option(None, "--metadata", "-m", help="Manifiesto YAML externo"),
    force: bool = typer.Option(False, "--force", "-f", help="Re-ingestar aunque ya exista"),
):
    """Ingesta un archivo de fuente jurídica en el kernel."""
    _ensure_db()
    if not file.exists():
        err_console.print(f"Archivo no encontrado: {file}")
        raise typer.Exit(1)
    try:
        result = tc.ingest_source(
            file_path=str(file),
            metadata_path=str(metadata) if metadata else None,
            force=force,
        )
        console.print(Panel(
            f"[bold green]Fuente ingresada[/bold green]\n"
            f"  ID: {result['source_id']}\n"
            f"  Título: {result['title']}\n"
            f"  Segmentos: {result['segments']}  Sub-segmentos: {result.get('sub_segments', 0)}",
            title="Ingesta exitosa",
            border_style="green",
        ))
    except DuplicateSourceError as e:
        console.print(Panel(
            f"[yellow]Esta fuente ya fue ingresada (source_id={e.existing_id}).[/yellow]\n"
            f"Usa [bold]--force[/bold] para re-ingestar.",
            title="Duplicado detectado",
            border_style="yellow",
        ))
        raise typer.Exit(0)
    except Exception as e:
        err_console.print(f"Error al ingestar: {e}")
        raise typer.Exit(1)


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------

@app.command(name="list")
def list_sources(
    source_type: Optional[str] = typer.Option(None, "--type", "-t", help="Filtrar por tipo"),
    topic: Optional[str] = typer.Option(None, "--topic", help="Filtrar por tema"),
):
    """Lista las fuentes disponibles en el kernel."""
    _ensure_db()
    sources = tc.list_sources(source_type=source_type, topic=topic)
    if not sources:
        console.print("[yellow]No hay fuentes. Usa 'legal-kernel ingest' para cargar.[/yellow]")
        return
    table = Table(box=box.SIMPLE_HEAD, show_lines=False)
    table.add_column("ID", style="cyan", width=4)
    table.add_column("Título", style="white", max_width=50)
    table.add_column("Tipo", style="magenta", width=12)
    table.add_column("Versión", style="dim", width=20)
    table.add_column("Estado", style="green", width=10)
    for s in sources:
        import json as _json
        topics = _json.loads(s.get("topics_json") or "[]")
        table.add_row(
            str(s["id"]),
            s["title"],
            s.get("source_type", "?"),
            s.get("version_label") or "—",
            s.get("status", "?"),
        )
    console.print(table)
    console.print(f"[dim]{len(sources)} fuente(s)[/dim]")


# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------

@app.command()
def search(
    query: str = typer.Argument(..., help="Texto a buscar"),
    source_type: Optional[str] = typer.Option(None, "--type", "-t"),
    limit: int = typer.Option(10, "--limit", "-n"),
):
    """Busca fuentes por texto, título o metadata."""
    _ensure_db()
    results = tc.search_sources(query, source_type=source_type, limit=limit)
    if not results:
        console.print(f"[yellow]Sin resultados para:[/yellow] {query!r}")
        return
    for r in results:
        console.print(Panel(
            f"[bold]{r['title']}[/bold]  [dim](tipo: {r['source_type']})[/dim]\n"
            f"[cyan]source_id={r['source_id']}[/cyan]  versión: {r.get('version_label') or '—'}\n\n"
            f"{r['snippet']}",
            border_style="blue",
        ))


# ---------------------------------------------------------------------------
# get
# ---------------------------------------------------------------------------

@app.command()
def get(
    source_id: int = typer.Option(..., "--source-id", help="ID de la fuente"),
    locator: Optional[str] = typer.Option(None, "--locator", "-l", help="Locator del segmento"),
    segment_id: Optional[int] = typer.Option(None, "--segment-id", help="ID del segmento"),
):
    """Obtiene un segmento por locator o ID."""
    _ensure_db()
    try:
        seg = tc.get_segment(
            source_id=source_id,
            locator=locator,
            segment_id=segment_id,
        )
    except ValueError as e:
        err_console.print(str(e))
        raise typer.Exit(1)

    console.print(Panel(
        f"[bold cyan]{seg.get('locator', '?')}[/bold cyan]  [dim](tipo: {seg.get('segment_type')})[/dim]\n\n"
        f"{seg['text']}\n\n"
        f"[dim]Cita sugerida:[/dim]\n{seg.get('suggested_citation') or '—'}",
        title=f"Segmento #{seg['id']}",
        border_style="cyan",
    ))


# ---------------------------------------------------------------------------
# cite
# ---------------------------------------------------------------------------

@app.command()
def cite(
    segment_id: int = typer.Option(..., "--segment-id", help="ID del segmento"),
):
    """Genera una cita verificable para un segmento."""
    _ensure_db()
    try:
        cit = tc.cite_segment(segment_id)
    except ValueError as e:
        err_console.print(str(e))
        raise typer.Exit(1)

    console.print(Panel(
        f"[bold]{cit['citation_text']}[/bold]\n\n"
        f"[dim]source_id={cit['source_id']}  segment_id={cit['segment_id']}  "
        f"confianza={cit['confidence']}[/dim]",
        title="Cita generada",
        border_style="green",
    ))


# ---------------------------------------------------------------------------
# compare
# ---------------------------------------------------------------------------

@app.command()
def compare(
    source_a: int = typer.Option(..., "--source-a"),
    source_b: int = typer.Option(..., "--source-b"),
):
    """Compara el texto normalizado de dos fuentes."""
    _ensure_db()
    try:
        result = tc.compare_sources(source_a, source_b)
    except ValueError as e:
        err_console.print(str(e))
        raise typer.Exit(1)

    if result["identical"]:
        console.print("[green]Los textos son idénticos.[/green]")
    else:
        console.print(Syntax(result["diff"], "diff", theme="ansi_dark", line_numbers=True))


# ---------------------------------------------------------------------------
# audit
# ---------------------------------------------------------------------------

@app.command()
def audit(
    entity_type: Optional[str] = typer.Option(None, "--type", "-t"),
    entity_id: Optional[str] = typer.Option(None, "--id"),
    limit: int = typer.Option(20, "--limit", "-n"),
):
    """Muestra el registro de auditoría."""
    _ensure_db()
    entries = tc.audit_trail(entity_type=entity_type, entity_id=entity_id, limit=limit)
    if not entries:
        console.print("[dim]Sin entradas de auditoría.[/dim]")
        return
    table = Table(box=box.SIMPLE_HEAD)
    table.add_column("ID", style="dim", width=5)
    table.add_column("Acción", style="cyan")
    table.add_column("Tipo", style="magenta")
    table.add_column("Entidad", style="yellow")
    table.add_column("Fecha", style="dim")
    for e in entries:
        table.add_row(
            str(e["id"]),
            e["action"],
            e.get("entity_type") or "—",
            e.get("entity_id") or "—",
            e.get("created_at") or "—",
        )
    console.print(table)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ensure_db():
    db_path = _db()
    if not db_path.exists():
        init_db(db_path)


if __name__ == "__main__":
    app()
