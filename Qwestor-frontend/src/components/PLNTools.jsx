const PLNTools = ({
  ingestInput,
  onIngestInputChange,
  onIngestSubmit,
  ingestLoading,
  ingestResult,
  ingestError,
  queryInput,
  onQueryInputChange,
  onQuerySubmit,
  queryLoading,
  queryResult,
  queryError,
  resetScope,
  onResetScopeChange,
  onResetSubmit,
  resetLoading,
  resetResult,
  resetError,
}) => {
  return (
    <aside className="pln-tools" aria-label="PLN-RAG tools">
      <h2>PLN-RAG Tools</h2>

      <section className="pln-card">
        <h3>Ingest</h3>
        <form className="pln-form" onSubmit={onIngestSubmit}>
          <textarea
            value={ingestInput}
            onChange={(event) => onIngestInputChange(event.target.value)}
            placeholder="One text per line"
            rows={5}
            disabled={ingestLoading}
          />
          <button type="submit" disabled={ingestLoading || !ingestInput.trim()}>
            {ingestLoading ? 'Ingesting...' : 'Ingest'}
          </button>
        </form>
        {ingestError && <p className="pln-error">{ingestError}</p>}
        {ingestResult && (
          <div className="pln-result">
            <p>Processed: {ingestResult.processed_count}</p>
            <ul>
              {ingestResult.results?.map((item, index) => (
                <li key={`${item.text}-${index}`}>
                  <strong>{item.status}</strong>: {item.text}
                  {item.error ? ` (${item.error})` : ''}
                </li>
              ))}
            </ul>
          </div>
        )}
      </section>

      <section className="pln-card">
        <h3>Query</h3>
        <form className="pln-form" onSubmit={onQuerySubmit}>
          <input
            type="text"
            value={queryInput}
            onChange={(event) => onQueryInputChange(event.target.value)}
            placeholder="Ask PLN-RAG"
            disabled={queryLoading}
          />
          <button type="submit" disabled={queryLoading || !queryInput.trim()}>
            {queryLoading ? 'Querying...' : 'Query'}
          </button>
        </form>
        {queryError && <p className="pln-error">{queryError}</p>}
        {queryResult && (
          <div className="pln-result">
            <p>
              <strong>Answer:</strong> {queryResult.answer}
            </p>
            <p>
              <strong>Status:</strong> {queryResult.query_status}
            </p>
            <p>
              <strong>PLN Query:</strong> {queryResult.pln_query}
            </p>
            <p>
              <strong>Executed Query:</strong> {queryResult.executed_query}
            </p>
            <p>
              <strong>Raw Proof:</strong> {queryResult.raw_proof || 'N/A'}
            </p>
            <div>
              <strong>Sources:</strong>
              {queryResult.sources?.length ? (
                <ul>
                  {queryResult.sources.map((source, index) => (
                    <li key={`${source}-${index}`}>{source}</li>
                  ))}
                </ul>
              ) : (
                <p>None</p>
              )}
            </div>
          </div>
        )}
      </section>

      <section className="pln-card">
        <h3>Reset</h3>
        <form className="pln-form pln-form-inline" onSubmit={onResetSubmit}>
          <select value={resetScope} onChange={(event) => onResetScopeChange(event.target.value)}>
            <option value="all">all</option>
            <option value="vectordb">vectordb</option>
            <option value="atomspace">atomspace</option>
          </select>
          <button type="submit" disabled={resetLoading}>
            {resetLoading ? 'Resetting...' : 'Reset'}
          </button>
        </form>
        {resetError && <p className="pln-error">{resetError}</p>}
        {resetResult && <p className="pln-success">Reset scope: {resetResult.scope}</p>}
      </section>
    </aside>
  )
}

export default PLNTools
