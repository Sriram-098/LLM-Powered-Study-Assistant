import jsPDF from 'jspdf'

export const generatePDF = (material, generatedData) => {
  const doc = new jsPDF()
  const pageWidth = doc.internal.pageSize.width
  const margin = 20
  const maxWidth = pageWidth - 2 * margin
  let yPosition = margin

  // Helper function to add text with word wrapping
  const addText = (text, fontSize = 12, isBold = false) => {
    doc.setFontSize(fontSize)
    if (isBold) {
      doc.setFont(undefined, 'bold')
    } else {
      doc.setFont(undefined, 'normal')
    }
    
    const lines = doc.splitTextToSize(text, maxWidth)
    
    // Check if we need a new page
    if (yPosition + (lines.length * fontSize * 0.5) > doc.internal.pageSize.height - margin) {
      doc.addPage()
      yPosition = margin
    }
    
    doc.text(lines, margin, yPosition)
    yPosition += lines.length * fontSize * 0.5 + 5
  }

  // Add header
  addText(`Study Material: ${material.title}`, 18, true)
  addText(`Generated on: ${new Date().toLocaleDateString()}`, 10)
  addText(`File Type: ${material.file_type.toUpperCase()}`, 10)
  addText(`Created: ${new Date(material.uploaded_at).toLocaleDateString()}`, 10)
  
  yPosition += 10

  // Add original content
  if (material.content) {
    addText('ORIGINAL CONTENT', 16, true)
    addText('_'.repeat(50), 10)
    addText(material.content, 11)
    yPosition += 10
  }

  // Add generated summary
  if (generatedData?.summary) {
    addText('AI-GENERATED SUMMARY', 16, true)
    addText('_'.repeat(50), 10)
    addText(generatedData.summary, 11)
    yPosition += 10
  }

  // Add quiz questions
  if (generatedData?.quiz_questions) {
    try {
      const quizData = JSON.parse(generatedData.quiz_questions)
      addText('QUIZ QUESTIONS', 16, true)
      addText('_'.repeat(50), 10)
      
      quizData.forEach((question, index) => {
        addText(`${index + 1}. ${question.question}`, 12, true)
        
        if (question.options) {
          question.options.forEach((option, optIndex) => {
            const letter = String.fromCharCode(65 + optIndex) // A, B, C, D
            addText(`   ${letter}. ${option}`, 11)
          })
        }
        
        if (question.correct_answer) {
          addText(`   Correct Answer: ${question.correct_answer}`, 11, true)
        }
        
        yPosition += 5
      })
    } catch (error) {
      addText('Quiz questions data could not be parsed', 11)
    }
  }

  // Add key concepts
  if (generatedData?.key_concepts) {
    try {
      const concepts = JSON.parse(generatedData.key_concepts)
      addText('KEY CONCEPTS', 16, true)
      addText('_'.repeat(50), 10)
      
      concepts.forEach((concept, index) => {
        addText(`${index + 1}. ${concept}`, 11)
      })
    } catch (error) {
      addText('Key concepts data could not be parsed', 11)
    }
  }

  // Save the PDF
  const fileName = `${material.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_study_material.pdf`
  doc.save(fileName)
}

export default generatePDF