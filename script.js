document.addEventListener('DOMContentLoaded', () => {
    const newNoteBtn = document.getElementById('newNote');
    const saveNoteBtn = document.getElementById('saveNote');
    const noteTitle = document.getElementById('noteTitle');
    const noteContent = document.getElementById('noteContent');

    // Create new note
    newNoteBtn.addEventListener('click', () => {
        if (noteContent.value && !confirm('Are you sure you want to create a new note? Current note will be lost.')) {
            return;
        }
        noteTitle.value = '';
        noteContent.value = '';
    });

    // Save note as .txt file
    saveNoteBtn.addEventListener('click', () => {
        if (!noteContent.value) {
            alert('Please write something before saving!');
            return;
        }

        const title = noteTitle.value || 'Untitled Note';
        const content = noteContent.value;
        const blob = new Blob([content], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        
        a.href = url;
        a.download = `${title}.txt`;
        document.body.appendChild(a);
        a.click();
        
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    });

    // Auto-save to localStorage
    const autoSave = () => {
        localStorage.setItem('noteTitle', noteTitle.value);
        localStorage.setItem('noteContent', noteContent.value);
    };

    // Load saved content from localStorage
    const loadSavedContent = () => {
        const savedTitle = localStorage.getItem('noteTitle');
        const savedContent = localStorage.getItem('noteContent');
        
        if (savedTitle) noteTitle.value = savedTitle;
        if (savedContent) noteContent.value = savedContent;
    };

    // Auto-save every 30 seconds
    setInterval(autoSave, 30000);
    
    // Save when content changes
    noteTitle.addEventListener('input', autoSave);
    noteContent.addEventListener('input', autoSave);

    // Load saved content when page loads
    loadSavedContent();
}); 