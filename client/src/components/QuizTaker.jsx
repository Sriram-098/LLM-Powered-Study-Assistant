import { useState, useEffect } from 'react'

const QuizTaker = ({ questions, onComplete, onCancel }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [answers, setAnswers] = useState({})
  const [showResults, setShowResults] = useState(false)
  const [timeLeft, setTimeLeft] = useState(null)
  const [quizStarted, setQuizStarted] = useState(false)

  // Timer functionality (optional - 30 seconds per question)
  useEffect(() => {
    if (quizStarted && timeLeft > 0 && !showResults) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000)
      return () => clearTimeout(timer)
    } else if (timeLeft === 0 && !showResults) {
      handleNextQuestion()
    }
  }, [timeLeft, quizStarted, showResults])

  const startQuiz = () => {
    setQuizStarted(true)
    setTimeLeft(30) // 30 seconds per question
  }

  const handleAnswerSelect = (answer) => {
    setAnswers(prev => ({
      ...prev,
      [currentQuestion]: answer
    }))
  }

  const handleNextQuestion = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1)
      setTimeLeft(30) // Reset timer for next question
    } else {
      finishQuiz()
    }
  }

  const handlePreviousQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1)
      setTimeLeft(30) // Reset timer
    }
  }

  const finishQuiz = () => {
    setShowResults(true)
    setTimeLeft(null)
  }

  const calculateScore = () => {
    let correct = 0
    questions.forEach((question, index) => {
      if (question.type === 'multiple_choice' || question.type === 'true_false') {
        if (answers[index] === question.correct_answer) {
          correct++
        }
      }
      // For short_answer questions, we'll mark them as correct if answered
      // In a real app, you'd want more sophisticated checking
      else if (question.type === 'short_answer' && answers[index]?.trim()) {
        correct++
      }
    })
    return { correct, total: questions.length, percentage: Math.round((correct / questions.length) * 100) }
  }

  const getScoreColor = (percentage) => {
    if (percentage >= 80) return 'text-gray-900'
    if (percentage >= 60) return 'text-gray-700'
    return 'text-gray-600'
  }

  const getScoreMessage = (percentage) => {
    if (percentage >= 90) return 'Excellent work!'
    if (percentage >= 80) return 'Great job!'
    if (percentage >= 70) return 'Good effort!'
    if (percentage >= 60) return 'Not bad, keep studying!'
    return 'Keep practicing!'
  }

  if (!quizStarted) {
    return (
      <div className="bg-white rounded-2xl shadow-xl border border-gray-200 p-8 text-center">
        <div className="mb-6">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-gray-900" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Ready to Take the Quiz?</h2>
          <p className="text-gray-600 mb-4">
            This quiz contains {questions.length} questions. You'll have 30 seconds per question.
          </p>
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6">
            <h3 className="font-semibold text-gray-900 mb-2">Quiz Instructions:</h3>
            <ul className="text-gray-700 text-sm space-y-1 text-left">
              <li>• Answer each question to the best of your ability</li>
              <li>• You can navigate back to previous questions</li>
              <li>• Timer will automatically move to next question</li>
              <li>• Review your answers before submitting</li>
            </ul>
          </div>
        </div>
        <div className="flex justify-center space-x-4">
          <button
            onClick={startQuiz}
            className="px-6 py-3 bg-black text-white rounded-lg font-semibold hover:bg-gray-800 transition-colors cursor-pointer"
          >
            <svg className="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Start Quiz
          </button>
          <button
            onClick={onCancel}
            className="px-6 py-3 bg-white text-gray-900 border-2 border-gray-300 rounded-lg font-semibold hover:bg-gray-50 transition-colors cursor-pointer"
          >
            Cancel
          </button>
        </div>
      </div>
    )
  }

  if (showResults) {
    const score = calculateScore()
    return (
      <div className="bg-white rounded-2xl shadow-xl border border-gray-200 p-8">
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-10 h-10 text-gray-900" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Quiz Complete!</h2>
          <p className="text-gray-600 mb-6">{getScoreMessage(score.percentage)}</p>
          
          <div className="bg-gray-50 rounded-xl p-6 mb-6">
            <div className="text-center">
              <div className={`text-4xl font-bold mb-2 ${getScoreColor(score.percentage)}`}>
                {score.percentage}%
              </div>
              <p className="text-gray-600">
                {score.correct} out of {score.total} questions correct
              </p>
            </div>
          </div>
        </div>

        {/* Detailed Results */}
        <div className="space-y-4 mb-8">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Review Your Answers:</h3>
          {questions.map((question, index) => {
            const userAnswer = answers[index]
            const isCorrect = (question.type === 'multiple_choice' || question.type === 'true_false')
              ? userAnswer === question.correct_answer
              : Boolean(userAnswer?.trim())

            return (
              <div key={index} className={`border rounded-lg p-4 ${isCorrect ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}`}>
                <div className="flex items-start mb-3">
                  <span className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold mr-3 ${
                    isCorrect ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
                  }`}>
                    {index + 1}
                  </span>
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900 mb-2">{question.question}</h4>
                    
                    {(question.type === 'multiple_choice' || question.type === 'true_false') && (
                      <div className="space-y-2">
                        <p className="text-sm">
                          <span className="font-medium">Your answer:</span> 
                          <span className={isCorrect ? 'text-green-700' : 'text-red-700'}>
                            {userAnswer || 'No answer'}
                          </span>
                        </p>
                        {!isCorrect && (
                          <p className="text-sm">
                            <span className="font-medium">Correct answer:</span> 
                            <span className="text-green-700">{question.correct_answer}</span>
                          </p>
                        )}
                        {question.explanation && (
                          <p className="text-sm">
                            <span className="font-medium">Explanation:</span> 
                            <span className="text-gray-600">{question.explanation}</span>
                          </p>
                        )}
                      </div>
                    )}
                    
                    {question.type === 'short_answer' && (
                      <div className="space-y-2">
                        <p className="text-sm">
                          <span className="font-medium">Your answer:</span> 
                          <span className="text-gray-700">{userAnswer || 'No answer'}</span>
                        </p>
                        {question.sample_answer && (
                          <p className="text-sm">
                            <span className="font-medium">Sample answer:</span> 
                            <span className="text-gray-600">{question.sample_answer}</span>
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                  
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                    isCorrect ? 'bg-green-500' : 'bg-red-500'
                  }`}>
                    {isCorrect ? (
                      <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    ) : (
                      <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        <div className="flex justify-center space-x-4">
          <button
            onClick={() => onComplete(score)}
            className="px-6 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition-colors"
          >
            Finish
          </button>
          <button
            onClick={() => {
              setShowResults(false)
              setQuizStarted(false)
              setCurrentQuestion(0)
              setAnswers({})
            }}
            className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 transition-colors"
          >
            Retake Quiz
          </button>
        </div>
      </div>
    )
  }

  const currentQ = questions[currentQuestion]
  const progress = ((currentQuestion + 1) / questions.length) * 100

  return (
    <div className="bg-white rounded-2xl shadow-xl border border-gray-200 p-8">
      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-600">
            Question {currentQuestion + 1} of {questions.length}
          </span>
          {timeLeft !== null && (
            <span className={`text-sm font-medium ${timeLeft <= 10 ? 'text-red-600' : 'text-gray-600'}`}>
              Time: {timeLeft}s
            </span>
          )}
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-purple-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>

      {/* Question */}
      <div className="mb-8">
        <h2 className="text-xl font-bold text-gray-900 mb-6">{currentQ.question}</h2>

        {currentQ.type === 'multiple_choice' && currentQ.options && (
          <div className="space-y-3">
            {currentQ.options.map((option, optionIndex) => (
              <button
                key={optionIndex}
                onClick={() => handleAnswerSelect(option)}
                className={`w-full text-left p-4 rounded-lg border-2 transition-colors cursor-pointer ${
                  answers[currentQuestion] === option
                    ? 'border-black bg-gray-100'
                    : 'border-gray-200 hover:border-gray-400 bg-white'
                }`}
              >
                <div className="flex items-center">
                  <span className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold mr-3 ${
                    answers[currentQuestion] === option
                      ? 'bg-black text-white'
                      : 'bg-gray-200 text-gray-700'
                  }`}>
                    {String.fromCharCode(65 + optionIndex)}
                  </span>
                  <span className="flex-1">{option}</span>
                </div>
              </button>
            ))}
          </div>
        )}

        {currentQ.type === 'true_false' && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <button
                onClick={() => handleAnswerSelect('True')}
                className={`p-6 rounded-lg border-2 transition-colors cursor-pointer ${
                  answers[currentQuestion] === 'True'
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-200 hover:border-green-300 bg-white'
                }`}
              >
                <div className="text-center">
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3 ${
                    answers[currentQuestion] === 'True'
                      ? 'bg-green-500 text-white'
                      : 'bg-gray-200 text-gray-700'
                  }`}>
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <span className="text-lg font-semibold text-gray-900">True</span>
                </div>
              </button>
              
              <button
                onClick={() => handleAnswerSelect('False')}
                className={`p-6 rounded-lg border-2 transition-colors cursor-pointer ${
                  answers[currentQuestion] === 'False'
                    ? 'border-red-500 bg-red-50'
                    : 'border-gray-200 hover:border-red-300 bg-white'
                }`}
              >
                <div className="text-center">
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3 ${
                    answers[currentQuestion] === 'False'
                      ? 'bg-red-500 text-white'
                      : 'bg-gray-200 text-gray-700'
                  }`}>
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </div>
                  <span className="text-lg font-semibold text-gray-900">False</span>
                </div>
              </button>
            </div>
          </div>
        )}

        {currentQ.type === 'short_answer' && (
          <textarea
            value={answers[currentQuestion] || ''}
            onChange={(e) => handleAnswerSelect(e.target.value)}
            placeholder="Type your answer here..."
            className="w-full p-4 border-2 border-gray-200 rounded-lg focus:border-purple-500 focus:outline-none resize-none"
            rows={4}
          />
        )}
      </div>

      {/* Navigation */}
      <div className="flex justify-between items-center">
        <button
          onClick={handlePreviousQuestion}
          disabled={currentQuestion === 0}
          className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Previous
        </button>

        <div className="flex space-x-3">
          <button
            onClick={onCancel}
            className="px-6 py-3 bg-red-100 text-red-700 rounded-lg font-semibold hover:bg-red-200 transition-colors"
          >
            Cancel Quiz
          </button>
          
          {currentQuestion === questions.length - 1 ? (
            <button
              onClick={finishQuiz}
              className="px-6 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition-colors"
            >
              Finish Quiz
            </button>
          ) : (
            <button
              onClick={handleNextQuestion}
              className="px-6 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition-colors"
            >
              Next Question
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default QuizTaker