"""
PDF Exporter Module - Professional PDF report generation
Generates beautiful, formatted PDF reports with statistics and categorized tasks
With comprehensive error handling and validation
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, 
        Spacer, KeepTogether
    )
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("ReportLab not installed")


class PDFExportError(Exception):
    """Raised when PDF export fails"""
    pass


class PDFExporter:
    """
    Professional PDF report generator for tasks
    Creates formatted, categorized task reports with statistics
    """
    
    # PDF Configuration
    PAGE_SIZE = letter
    MARGIN = 0.5 * inch
    
    # Color scheme
    COLORS = {
        'primary': '#1f4788',
        'secondary': '#2c5aa0',
        'accent': '#4a7ba7',
        'background': '#f0f0f0',
        'border': '#000000'
    }
    
    def __init__(self):
        """Initialize PDF exporter"""
        if not REPORTLAB_AVAILABLE:
            logger.warning("ReportLab not available for PDF export")
        self.available = REPORTLAB_AVAILABLE
    
    def export_tasks_to_pdf(self, 
                           tasks: List[Dict], 
                           filename: Optional[str] = None,
                           include_completed: bool = True) -> Optional[str]:
        """
        Export tasks to a professional PDF report
        
        Args:
            tasks: List of task dictionaries to export
            filename: Output filename (auto-generated if None)
            include_completed: Whether to include completed tasks
            
        Returns:
            Path to generated PDF file or None if error
        """
        if not self.available:
            logger.error("ReportLab not available")
            print("❌ ReportLab not installed. Install with: pip install reportlab")
            return None
        
        if not tasks:
            logger.warning("No tasks to export")
            print("⚠️  No tasks to export")
            return None
        
        try:
            # Validate and prepare tasks
            filtered_tasks = self._filter_tasks(tasks, include_completed)
            if not filtered_tasks:
                print("⚠️  No tasks to export (all filtered out)")
                return None
            
            # Generate filename if not provided
            if not filename:
                filename = f"task_report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf"
            
            # Validate filename
            if not self._validate_filename(filename):
                raise PDFExportError("Invalid filename")
            
            # Create PDF document
            pdf = SimpleDocTemplate(
                filename,
                pagesize=self.PAGE_SIZE,
                rightMargin=self.MARGIN,
                leftMargin=self.MARGIN,
                topMargin=self.MARGIN,
                bottomMargin=self.MARGIN
            )
            
            story = []
            styles = getSampleStyleSheet()
            
            # Add content
            story.extend(self._create_header(styles))
            story.extend(self._create_statistics(filtered_tasks, styles))
            story.extend(self._create_task_tables(filtered_tasks, styles))
            story.extend(self._create_footer(styles))
            
            # Build PDF
            logger.info(f"Building PDF: {filename}")
            pdf.build(story)
            
            file_size = os.path.getsize(filename) / 1024  # KB
            logger.info(f"PDF exported successfully: {filename} ({file_size:.1f} KB)")
            print(f"✅ PDF exported successfully: {filename}")
            
            return filename
            
        except PDFExportError as e:
            logger.error(f"PDF export error: {e}")
            print(f"❌ Export error: {e}")
            return None
        except PermissionError:
            logger.error(f"Permission denied writing to {filename}")
            print(f"❌ Permission denied: Cannot write to {filename}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error exporting PDF: {e}")
            print(f"❌ Error exporting PDF: {e}")
            return None
    
    def _filter_tasks(self, tasks: List[Dict], include_completed: bool) -> List[Dict]:
        """Filter and validate tasks"""
        filtered = []
        for task in tasks:
            if not include_completed and task.get("completed"):
                continue
            
            # Validate task structure
            if not isinstance(task, dict) or "title" not in task:
                logger.warning(f"Invalid task structure: {task}")
                continue
            
            filtered.append(task)
        
        return filtered
    
    def _validate_filename(self, filename: str) -> bool:
        """Validate PDF filename"""
        if not filename or not filename.endswith('.pdf'):
            logger.warning(f"Invalid filename: {filename}")
            return False
        
        # Check for invalid characters
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
        if any(char in filename for char in invalid_chars):
            logger.warning(f"Filename contains invalid characters: {filename}")
            return False
        
        return True
    
    def _create_header(self, styles) -> List:
        """Create PDF header with title and metadata"""
        story = []
        
        # Custom title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor(self.COLORS['primary']),
            spaceAfter=10,
            alignment=1  # Center
        )
        
        story.append(Paragraph("📋 Task Manager Report", title_style))
        story.append(Spacer(1, 0.2 * inch))
        
        # Metadata
        report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        metadata = f"<b>Generated:</b> {report_date}"
        story.append(Paragraph(metadata, styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))
        
        return story
    
    def _create_statistics(self, tasks: List[Dict], styles) -> List:
        """Create statistics section"""
        story = []
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor(self.COLORS['secondary']),
            spaceAfter=12,
            spaceBefore=6
        )
        
        story.append(Paragraph("📊 Summary Statistics", heading_style))
        
        stats = self._calculate_stats(tasks)
        stats_text = f"""
        <b>Total Tasks:</b> {stats['total']}<br/>
        <b>Completed:</b> {stats['completed']} ✅<br/>
        <b>Pending:</b> {stats['pending']} ⭕<br/>
        <b>Completion Rate:</b> {stats['progress']:.1f}%
        """
        
        story.append(Paragraph(stats_text, styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))
        
        return story
    
    def _create_task_tables(self, tasks: List[Dict], styles) -> List:
        """Create categorized task tables"""
        story = []
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor(self.COLORS['secondary']),
            spaceAfter=10,
            spaceBefore=10
        )
        
        # Group tasks by category
        categories = {}
        for task in tasks:
            category = task.get('category', 'General')
            if category not in categories:
                categories[category] = []
            categories[category].append(task)
        
        # Create table for each category
        for category in sorted(categories.keys()):
            story.append(Paragraph(f"📂 {category}", heading_style))
            
            # Build table data
            table_data = [['ID', 'Task', 'Status', 'Created']]
            
            for task in categories[category]:
                task_id = str(task.get('id', ''))
                title = task.get('title', 'Untitled')[:50]
                status = '✅' if task.get('completed') else '⭕'
                created = task.get('created_at', '')[:10]
                
                table_data.append([task_id, title, status, created])
            
            # Create styled table
            table = Table(
                table_data,
                colWidths=[0.5*inch, 3.2*inch, 0.8*inch, 1.2*inch]
            )
            
            table.setStyle(TableStyle([
                # Header style
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.COLORS['secondary'])),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                
                # Data rows style
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), 
                 [colors.white, colors.HexColor(self.COLORS['background'])]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(self.COLORS['border'])),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(table)
            story.append(Spacer(1, 0.2 * inch))
        
        return story
    
    def _create_footer(self, styles) -> List:
        """Create PDF footer"""
        story = []
        story.append(Spacer(1, 0.4 * inch))
        
        footer_text = "Generated by Smart Task Manager 🎯 | Made with ❤️"
        story.append(Paragraph(footer_text, styles['Normal']))
        
        return story
    
    def _calculate_stats(self, tasks: List[Dict]) -> Dict:
        """Calculate task statistics"""
        total = len(tasks)
        completed = sum(1 for t in tasks if t.get('completed', False))
        pending = total - completed
        progress = (completed / total * 100) if total > 0 else 0
        
        return {
            'total': total,
            'completed': completed,
            'pending': pending,
            'progress': progress
        }
    
    @staticmethod
    def is_available() -> bool:
        """Check if PDF export is available"""
        return REPORTLAB_AVAILABLE
