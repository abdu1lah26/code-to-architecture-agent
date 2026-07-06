/**
 * Custom hook for Q&A management.
 */

import { useState, useCallback } from "react";
import { QAMessage, AnswerResponse } from "../types";
import { apiClient } from "../api/client";

interface UseQAState {
  messages: QAMessage[];
  loading: boolean;
  error: string | null;
}

export function useQA() {
  const [state, setState] = useState<UseQAState>({
    messages: [],
    loading: false,
    error: null,
  });

  /**
   * Ask a question.
   */
  const askQuestion = useCallback(
    async (jobId: string, question: string) => {
      // Add question to messages
      const questionId = `q_${Date.now()}`;
      const questionMessage: QAMessage = {
        id: questionId,
        type: "question",
        content: question,
        timestamp: new Date(),
      };

      setState((s) => ({
        ...s,
        messages: [...s.messages, questionMessage],
        loading: true,
        error: null,
      }));

      try {
        // Get answer from API
        const result = await apiClient.askQuestion(jobId, question);

        // Add answer to messages
        const answerId = `a_${Date.now()}`;
        const answerMessage: QAMessage = {
          id: answerId,
          type: "answer",
          content: result.answer,
          retrieved_chunks: result.retrieved_chunks,
          timestamp: new Date(),
        };

        setState((s) => ({
          ...s,
          messages: [...s.messages, answerMessage],
          loading: false,
        }));

        return result;
      } catch (error) {
        const errorMsg = error instanceof Error ? error.message : "Unknown error";
        setState((s) => ({
          ...s,
          error: errorMsg,
          loading: false,
        }));
        throw error;
      }
    },
    []
  );

  /**
   * Clear messages.
   */
  const clearMessages = useCallback(() => {
    setState({ messages: [], loading: false, error: null });
  }, []);

  return {
    ...state,
    askQuestion,
    clearMessages,
  };
}