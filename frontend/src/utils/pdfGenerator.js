import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

export async function generateReport(data) {
  const { title, predictions, chartElement } = data;
  const pdf = new jsPDF('p', 'mm', 'a4');

  // 封面
  pdf.setFontSize(24);
  pdf.text(title || '时序预测分析报告', 105, 60, { align: 'center' });
  pdf.setFontSize(12);
  pdf.text(`生成日期: ${new Date().toLocaleDateString('zh-CN')}`, 105, 80, { align: 'center' });
  pdf.text('鼠先知智能预测平台', 105, 90, { align: 'center' });

  // 预测结果页
  pdf.addPage();
  pdf.setFontSize(16);
  pdf.text('预测结果', 20, 20);

  if (chartElement) {
    const canvas = await html2canvas(chartElement, { scale: 2 });
    const imgData = canvas.toDataURL('image/png');
    pdf.addImage(imgData, 'PNG', 20, 30, 170, 100);
  }

  // 模型说明
  pdf.setFontSize(12);
  pdf.text('模型说明:', 20, 140);
  pdf.setFontSize(10);
  pdf.text('智能预测引擎基于数据特征自动路由选择最优算法', 20, 150);
  pdf.text('包含统计模型与深度学习模型的集成预测', 20, 158);

  return pdf;
}
