const METAMO_BASE_URL = import.meta.env.VITE_METAMO_BASE_URL || '/metamo'
const PLNRAG_BASE_URL = import.meta.env.VITE_PLNRAG_BASE_URL || '/plnrag'

const parseResponseBody = async (response) => {
  const contentType = response.headers.get('content-type') || ''

  if (contentType.includes('application/json')) {
    return response.json()
  }

  const text = await response.text()
  return text ? { message: text } : {}
}

const createError = (status, payload, fallbackMessage) => {
  const detail =
    payload?.detail || payload?.message || payload?.error || fallbackMessage || 'Request failed'
  return new Error(typeof detail === 'string' ? detail : JSON.stringify(detail))
}

const request = async (url, options = {}) => {
  let response

  try {
    response = await fetch(url, options)
  } catch {
    throw new Error('Network error. Check backend availability and CORS.')
  }

  const payload = await parseResponseBody(response)

  if (!response.ok) {
    throw createError(response.status, payload, `Request failed (${response.status})`)
  }

  return payload
}

export const apiConfig = {
  metamoBaseUrl: METAMO_BASE_URL,
  plnragBaseUrl: PLNRAG_BASE_URL,
}

export const sendChat = async ({ query, session_id }) => {
  return request(`${METAMO_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query, session_id }),
  })
}

export const ingestTexts = async (texts) => {
  return request(`${PLNRAG_BASE_URL}/ingest`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ texts }),
  })
}

export const queryPln = async (question) => {
  return request(`${PLNRAG_BASE_URL}/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question }),
  })
}

export const resetPln = async (scope) => {
  return request(`${PLNRAG_BASE_URL}/reset`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ scope }),
  })
}

export const getPlnHealth = async () => {
  return request(`${PLNRAG_BASE_URL}/health`)
}
