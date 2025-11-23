"""
CLI Dashboard - Visual analytics dashboard using rich library
Displays productivity trends, mood correlations, and insights
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich import box
import sys
import pathlib

try:
    # Normal package-relative imports (work when used as package)
    from .analytics_engine import get_analytics_engine
    from database import Task, MoodEntry, ProductivityEntry, Habit
    from .focus_tracker import get_focus_tracker
except Exception:
    # Likely running the file directly; add project root and retry with absolute imports
    project_root = pathlib.Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(project_root))
    from backend.modules.analytics_engine import get_analytics_engine
    from database import Task, MoodEntry, ProductivityEntry, Habit
    from backend.modules.focus_tracker import get_focus_tracker

console = Console()


class Dashboard:
    """CLI Dashboard for productivity analytics"""
    
    def __init__(self):
        self.analytics = get_analytics_engine()
        self.focus_tracker = get_focus_tracker()
    
    def display_daily_summary(self, date: Optional[str] = None):
        """Display daily summary dashboard"""
        if date is None:
            date = datetime.now().date().isoformat()
        
        daily_data = self.analytics.get_daily_aggregate(date)
        
        # Create main panel
        summary_text = Text()
        summary_text.append("[DAILY SUMMARY]\n\n", style="bold cyan")
        
        # Tasks
        completion_rate = (daily_data['tasks_completed'] / daily_data['tasks_planned'] * 100) if daily_data['tasks_planned'] > 0 else 0
        summary_text.append(f"[*] Tasks: ", style="green")
        summary_text.append(f"{daily_data['tasks_completed']}/{daily_data['tasks_planned']} ", style="bold")
        summary_text.append(f"({completion_rate:.1f}%)\n", style="dim")
        
        # Productivity
        if daily_data['productivity_score']:
            summary_text.append(f"[*] Productivity: ", style="blue")
            summary_text.append(f"{daily_data['productivity_score']:.1f}/100\n", style="bold")
        
        # Focus
        summary_text.append(f"[*] Focus Hours: ", style="yellow")
        summary_text.append(f"{daily_data['focus_hours']:.1f} hours\n", style="bold")
        summary_text.append(f"[*] Sessions: ", style="yellow")
        summary_text.append(f"{daily_data['focus_sessions']}\n", style="bold")
        
        # Mood
        if daily_data['mood_score']:
            summary_text.append(f"[*] Mood: ", style="magenta")
            summary_text.append(f"{daily_data['mood_score']}/10", style="bold")
            mood_entry = MoodEntry.get_today()
            if mood_entry and mood_entry.mood_text:
                summary_text.append(f" ({mood_entry.mood_text})\n", style="dim")
            else:
                summary_text.append("\n")
        
        # Focus score
        if daily_data['avg_focus_score']:
            summary_text.append(f"[*] Avg Focus Score: ", style="cyan")
            summary_text.append(f"{daily_data['avg_focus_score']:.1f}/10\n", style="bold")
        
        console.print(Panel(summary_text, title=f"Date: {date}", border_style="cyan"))
    
    def display_weekly_trends(self, start_date: Optional[str] = None):
        """Display weekly trends table"""
        weekly_data = self.analytics.get_weekly_aggregate(start_date)
        
        # Create table
        table = Table(title="Weekly Trends", show_header=True, header_style="bold cyan", box=box.ROUNDED)
        table.add_column("Date", style="cyan", width=12)
        table.add_column("Tasks", justify="center", width=10)
        table.add_column("Productivity", justify="center", width=12)
        table.add_column("Focus Hrs", justify="center", width=10)
        table.add_column("Mood", justify="center", width=8)
        
        for daily in weekly_data['daily_aggregates']:
            date_str = daily['date']
            # Format date for display
            date_obj = datetime.fromisoformat(date_str).date()
            display_date = date_obj.strftime("%m/%d")
            
            tasks_str = f"{daily['tasks_completed']}/{daily['tasks_planned']}"
            prod_str = f"{daily['productivity_score']:.1f}" if daily['productivity_score'] else "N/A"
            focus_str = f"{daily['focus_hours']:.1f}"
            mood_str = f"{daily['mood_score']}" if daily['mood_score'] else "N/A"
            
            table.add_row(display_date, tasks_str, prod_str, focus_str, mood_str)
        
        # Add summary row
        table.add_section()
        table.add_row(
            "AVERAGE",
            f"{weekly_data['total_tasks_completed']}/{weekly_data['total_tasks_planned']}",
            f"{weekly_data['avg_productivity_score']:.1f}" if weekly_data['avg_productivity_score'] else "N/A",
            f"{weekly_data['avg_daily_focus_hours']:.1f}",
            f"{weekly_data['avg_mood_score']:.1f}" if weekly_data['avg_mood_score'] else "N/A",
            style="bold"
        )
        
        console.print(table)
    
    def display_productivity_chart(self, days: int = 7):
        """Display ASCII productivity chart"""
        trends = self.analytics.get_trends(days=days)
        
        if not trends['daily_data']:
            console.print("[yellow]No data available for chart[/yellow]")
            return
        
        # Create chart
        chart_text = Text()
        chart_text.append(f"Productivity Trend ({days} days)\n\n", style="bold cyan")
        
        # Get productivity scores
        scores = []
        dates = []
        for daily in trends['daily_data']:
            if daily['productivity_score']:
                scores.append(float(daily['productivity_score']))
                date_obj = datetime.fromisoformat(daily['date']).date()
                dates.append(date_obj.strftime("%m/%d"))
        
        if not scores:
            chart_text.append("No productivity data available", style="dim")
            console.print(Panel(chart_text, border_style="cyan"))
            return
        
        # Create ASCII bar chart
        max_score = float(max(scores)) if scores else 100.0
        chart_height = 10
        
        # Draw chart
        for row in range(chart_height, 0, -1):
            threshold = (float(row) / float(chart_height)) * max_score
            line = ""
            for score in scores:
                if score >= threshold:
                    line += "# "
                else:
                    line += "  "
            chart_text.append(f"{threshold:3.0f}| {line}\n", style="dim")
        
        # X-axis labels
        chart_text.append("    " + "-" * (len(scores) * 2) + "\n", style="dim")
        chart_text.append("    ")
        for date in dates:
            chart_text.append(date[:5].ljust(3), style="dim")
        chart_text.append("\n")
        
        console.print(Panel(chart_text, border_style="cyan"))
    
    def display_mood_productivity_correlation(self, days: int = 30):
        """Display mood vs productivity correlation"""
        trends = self.analytics.get_trends(days=days)
        
        correlation = trends.get('mood_productivity_correlation')
        
        panel_text = Text()
        panel_text.append("Mood-Productivity Correlation\n\n", style="bold cyan")
        
        if correlation is not None:
            panel_text.append(f"Correlation Coefficient: ", style="yellow")
            panel_text.append(f"{correlation:.3f}\n\n", style="bold")
            
            if correlation > 0.5:
                panel_text.append("Strong positive correlation - mood significantly affects productivity!\n", style="green")
            elif correlation > 0.2:
                panel_text.append("Moderate positive correlation - mood has some impact on productivity.\n", style="yellow")
            elif correlation > -0.2:
                panel_text.append("Weak correlation - mood and productivity are relatively independent.\n", style="dim")
            else:
                panel_text.append("Negative correlation - interesting pattern detected.\n", style="red")
        else:
            panel_text.append("Not enough data to calculate correlation.\n", style="dim")
            panel_text.append("Need at least 2 days with both mood and productivity data.", style="dim")
        
        console.print(Panel(panel_text, border_style="cyan"))
    
    def display_habits_streaks(self):
        """Display habit streaks"""
        habits = Habit.get_all()
        
        if not habits:
            console.print("[dim]No habits tracked yet.[/dim]")
            return
        
        table = Table(title="Habit Streaks", show_header=True, header_style="bold cyan", box=box.ROUNDED)
        table.add_column("Habit", style="cyan")
        table.add_column("Frequency", justify="center")
        table.add_column("Streak", justify="center", style="bold yellow")
        
        for habit in habits:
            streak_indicator = "[ACTIVE]" if habit.streak_count > 0 else "[INACTIVE]"
            table.add_row(
                habit.name,
                habit.frequency,
                f"{streak_indicator} {habit.streak_count}"
            )
        
        console.print(table)
    
    def display_full_dashboard(self, date: Optional[str] = None):
        """Display full dashboard with all sections"""
        console.clear()
        console.print("\n[bold cyan]" + "=" * 60 + "[/bold cyan]")
        console.print("[bold cyan]  [bold white]NeuroMate Productivity Dashboard[/bold white][/bold cyan]")
        console.print("[bold cyan]" + "=" * 60 + "[/bold cyan]\n")
        
        # Daily summary
        self.display_daily_summary(date)
        console.print()
        
        # Weekly trends
        self.display_weekly_trends()
        console.print()
        
        # Productivity chart
        self.display_productivity_chart(days=7)
        console.print()
        
        # Mood-productivity correlation
        self.display_mood_productivity_correlation(days=30)
        console.print()
        
        # Habit streaks
        self.display_habits_streaks()
        console.print()
    
    def export_daily_summary(self, date: Optional[str] = None, format: str = "json") -> str:
        """
        Export daily summary to file
        
        Args:
            date: Date to export (defaults to today)
            format: Export format ("json" or "txt")
            
        Returns:
            File path of exported file
        """
        import json
        
        if date is None:
            date = datetime.now().date().isoformat()
        
        daily_data = self.analytics.get_daily_aggregate(date)
        
        if format == "json":
            filename = f"daily_summary_{date}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(daily_data, f, indent=2, ensure_ascii=False)
        else:  # txt
            filename = f"daily_summary_{date}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Daily Summary - {date}\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Tasks Completed: {daily_data['tasks_completed']}/{daily_data['tasks_planned']}\n")
                if daily_data['productivity_score']:
                    f.write(f"Productivity Score: {daily_data['productivity_score']:.1f}/100\n")
                f.write(f"Focus Hours: {daily_data['focus_hours']:.1f}\n")
                if daily_data['mood_score']:
                    f.write(f"Mood Score: {daily_data['mood_score']}/10\n")
                f.write(f"Focus Sessions: {daily_data['focus_sessions']}\n")
        
        return filename


# Global dashboard instance
_dashboard: Optional[Dashboard] = None


def get_dashboard() -> Dashboard:
    """Get or create global dashboard instance"""
    global _dashboard
    if _dashboard is None:
        _dashboard = Dashboard()
    return _dashboard

