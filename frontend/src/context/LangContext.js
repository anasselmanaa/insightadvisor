import { createContext, useContext } from 'react'
import { translations } from '../i18n'

export const LangContext = createContext('EN')
export const useLang = () => useContext(LangContext)

// TContext provides the t() function directly
export const TContext = createContext((key) => key)
export const useT2 = () => useContext(TContext)