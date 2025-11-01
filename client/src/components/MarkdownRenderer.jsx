import React from 'react'

const MarkdownRenderer = ({ content }) => {
  if (!content) return null

  // Simple markdown to HTML converter for our specific format
  const renderMarkdown = (text) => {
    let html = text
    
    // Convert headers with emojis
    html = html.replace(/^## (📋|🎯|📚|💡|🔍)(.*$)/gm, '<h2 class="text-xl font-bold text-gray-900 mb-4 mt-6 first:mt-0 flex items-center"><span class="mr-2">$1</span>$2</h2>')
    html = html.replace(/^### (.*$)/gm, '<h3 class="text-lg font-semibold text-gray-800 mb-3 mt-5">$1</h3>')
    html = html.replace(/^## (.*$)/gm, '<h2 class="text-xl font-bold text-gray-900 mb-4 mt-6 first:mt-0">$1</h2>')
    
    // Convert bold text
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>')
    
    // Convert bullet points
    html = html.replace(/^• (.*$)/gm, '<li class="mb-2 text-gray-700">$1</li>')
    
    // Convert numbered lists
    html = html.replace(/^(\d+)\. (.*$)/gm, '<li class="mb-2 text-gray-700">$2</li>')
    
    // Wrap consecutive bullet list items in ul tags
    html = html.replace(/(<li class="mb-2 text-gray-700">.*?<\/li>\s*)+/gs, (match) => {
      if (match.includes('•')) {
        return `<ul class="mb-4 ml-4 space-y-1">${match}</ul>`
      }
      return `<ol class="mb-4 ml-4 space-y-1 list-decimal">${match}</ol>`
    })
    
    // Handle horizontal rules
    html = html.replace(/^---$/gm, '<hr class="my-6 border-gray-300" />')
    
    // Convert paragraphs - split by double newlines
    const paragraphs = html.split(/\n\s*\n/)
    html = paragraphs.map(para => {
      para = para.trim()
      if (!para) return ''
      
      // Skip if it's already HTML (headers, lists, etc.)
      if (para.startsWith('<')) return para
      
      // Convert single newlines to spaces within paragraphs
      para = para.replace(/\n/g, ' ')
      
      return `<p class="mb-4 text-gray-700 leading-relaxed">${para}</p>`
    }).join('')
    
    return html
  }

  return (
    <div 
      className="prose prose-gray max-w-none"
      dangerouslySetInnerHTML={{ __html: renderMarkdown(content) }}
    />
  )
}

export default MarkdownRenderer