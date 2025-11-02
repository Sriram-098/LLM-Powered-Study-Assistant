import { describe, it, expect, vi, beforeEach } from 'vitest'
import { generatePDF } from '../pdfGenerator'
import jsPDF from 'jspdf'

// Mock jsPDF
vi.mock('jspdf', () => {
  const mockDoc = {
    internal: {
      pageSize: {
        width: 210,
        height: 297
      }
    },
    setFontSize: vi.fn(),
    setFont: vi.fn(),
    splitTextToSize: vi.fn((text) => [text]),
    text: vi.fn(),
    addPage: vi.fn(),
    save: vi.fn()
  }

  return {
    default: vi.fn(() => mockDoc)
  }
})

describe('pdfGenerator', () => {
  let mockDoc

  beforeEach(() => {
    vi.clearAllMocks()
    mockDoc = new jsPDF()
  })

  describe('generatePDF', () => {
    it('generates PDF with material title and basic info', () => {
      const material = {
        title: 'Test Material',
        file_type: 'pdf',
        uploaded_at: '2024-01-01T00:00:00Z',
        content: 'Test content'
      }

      generatePDF(material, null)

      expect(mockDoc.setFontSize).toHaveBeenCalled()
      expect(mockDoc.text).toHaveBeenCalled()
      expect(mockDoc.save).toHaveBeenCalledWith(
        expect.stringContaining('test_material_study_material.pdf')
      )
    })

    it('includes original content in PDF', () => {
      const material = {
        title: 'Test Material',
        file_type: 'text',
        uploaded_at: '2024-01-01T00:00:00Z',
        content: 'This is the original content'
      }

      generatePDF(material, null)

      expect(mockDoc.text).toHaveBeenCalledWith(
        expect.arrayContaining(['This is the original content']),
        expect.any(Number),
        expect.any(Number)
      )
    })

    it('includes AI-generated summary when provided', () => {
      const material = {
        title: 'Test Material',
        file_type: 'text',
        uploaded_at: '2024-01-01T00:00:00Z',
        content: 'Content'
      }

      const generatedData = {
        summary: 'This is an AI-generated summary'
      }

      generatePDF(material, generatedData)

      expect(mockDoc.text).toHaveBeenCalledWith(
        expect.arrayContaining(['This is an AI-generated summary']),
        expect.any(Number),
        expect.any(Number)
      )
    })

    it('includes quiz questions when provided', () => {
      const material = {
        title: 'Test Material',
        file_type: 'text',
        uploaded_at: '2024-01-01T00:00:00Z',
        content: 'Content'
      }

      const generatedData = {
        quiz_questions: JSON.stringify([
          {
            question: 'What is 2+2?',
            options: ['3', '4', '5', '6'],
            correct_answer: '4'
          }
        ])
      }

      generatePDF(material, generatedData)

      expect(mockDoc.text).toHaveBeenCalledWith(
        expect.arrayContaining(['1. What is 2+2?']),
        expect.any(Number),
        expect.any(Number)
      )
    })

    it('includes key concepts when provided', () => {
      const material = {
        title: 'Test Material',
        file_type: 'text',
        uploaded_at: '2024-01-01T00:00:00Z',
        content: 'Content'
      }

      const generatedData = {
        key_concepts: JSON.stringify(['Concept 1', 'Concept 2', 'Concept 3'])
      }

      generatePDF(material, generatedData)

      expect(mockDoc.text).toHaveBeenCalledWith(
        expect.arrayContaining(['1. Concept 1']),
        expect.any(Number),
        expect.any(Number)
      )
    })

    it('handles invalid JSON in quiz_questions gracefully', () => {
      const material = {
        title: 'Test Material',
        file_type: 'text',
        uploaded_at: '2024-01-01T00:00:00Z',
        content: 'Content'
      }

      const generatedData = {
        quiz_questions: 'invalid json'
      }

      expect(() => generatePDF(material, generatedData)).not.toThrow()
      expect(mockDoc.save).toHaveBeenCalled()
    })

    it('handles invalid JSON in key_concepts gracefully', () => {
      const material = {
        title: 'Test Material',
        file_type: 'text',
        uploaded_at: '2024-01-01T00:00:00Z',
        content: 'Content'
      }

      const generatedData = {
        key_concepts: 'invalid json'
      }

      expect(() => generatePDF(material, generatedData)).not.toThrow()
      expect(mockDoc.save).toHaveBeenCalled()
    })

    it('sanitizes filename by removing special characters', () => {
      const material = {
        title: 'Test Material: With Special! Characters?',
        file_type: 'text',
        uploaded_at: '2024-01-01T00:00:00Z',
        content: 'Content'
      }

      generatePDF(material, null)

      expect(mockDoc.save).toHaveBeenCalledWith(
        expect.stringMatching(/^test_material.*\.pdf$/)
      )
    })

    it('generates complete PDF with all sections', () => {
      const material = {
        title: 'Complete Test',
        file_type: 'pdf',
        uploaded_at: '2024-01-01T00:00:00Z',
        content: 'Original content here'
      }

      const generatedData = {
        summary: 'AI summary',
        quiz_questions: JSON.stringify([
          {
            question: 'Question 1?',
            options: ['A', 'B', 'C', 'D'],
            correct_answer: 'B'
          }
        ]),
        key_concepts: JSON.stringify(['Concept A', 'Concept B'])
      }

      generatePDF(material, generatedData)

      expect(mockDoc.setFontSize).toHaveBeenCalled()
      expect(mockDoc.setFont).toHaveBeenCalled()
      expect(mockDoc.text).toHaveBeenCalled()
      expect(mockDoc.save).toHaveBeenCalled()
    })
  })
})
