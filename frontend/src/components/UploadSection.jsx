function UploadSection({
  fileInputRef,
  uploaded,
  uploading,
  filename,
  isDragging,
  error,
  onFileChange,
  onChooseFile,
  onDrop,
  onDragOver,
  onDragLeave,
}) {
  return (
    <section
      className={`upload-section ${isDragging ? 'drag-active' : ''} ${uploaded ? 'upload-ready' : ''}`}
      onDrop={onDrop}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      aria-label="PDF upload"
    >
      <input
        ref={fileInputRef}
        className="visually-hidden"
        type="file"
        accept="application/pdf,.pdf"
        onChange={onFileChange}
        aria-label="Choose a PDF file"
      />

      <div className="upload-illustration" aria-hidden="true">
        <div className="document-sheet">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>

      <div className="upload-content">
        <h2>{uploaded ? 'Document ready' : 'Start chatting with your documents'}</h2>
        <p>
          {uploaded
            ? filename
            : 'Upload a PDF and ask questions using AI-powered search.'}
        </p>
      </div>

      <div className="upload-actions">
        <button className="button button-secondary" type="button" onClick={onChooseFile} disabled={uploading}>
          {uploaded ? 'Replace PDF' : 'Choose PDF'}
        </button>
        {uploading && (
          <div className="upload-status" role="status">
            <span className="spinner" aria-hidden="true"></span>
            Processing PDF
          </div>
        )}
        {uploaded && !uploading && <div className="ready-note">PDF Ready</div>}
      </div>

      {error && (
        <div className="error-message" role="alert">
          {error}
        </div>
      )}
    </section>
  )
}

export default UploadSection
