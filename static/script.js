// Define all global variables and functions
let currentNoteId = null;
let noteTitle, noteContent, journalDate, notesList;

const clearEditor = () => {
    currentNoteId = null;
    noteTitle.value = '';
    noteContent.value = '';
    journalDate.valueAsDate = new Date();
};

// Auto-resize textarea helper function
const autoResizeTextarea = (textarea) => {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
};

// Load note function (moved outside)
async function loadNote(noteId) {
    try {
        const response = await fetch(`/api/notes/${noteId}`);
        if (!response.ok) {
            throw new Error('Failed to load note');
        }
        const note = await response.json();
        displayNote(note);
    } catch (error) {
        console.error('Error loading note:', error);
        alert('Failed to load note. Please try again.');
    }
}

const deleteNote = async (noteId) => {
    if (!confirm('Are you sure you want to delete this note? This cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch(`/api/notes/${noteId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error('Failed to delete note');
        }

        // Remove the note from the list
        const noteElement = document.querySelector(`[data-note-id="${noteId}"]`);
        if (noteElement) {
            noteElement.remove();
        }

        // Clear the editor if the deleted note was being edited
        if (currentNoteId === noteId) {
            clearEditor();
        }

    } catch (error) {
        console.error('Delete failed:', error);
        alert('Failed to delete note: ' + error.message);
    }
};

document.addEventListener('DOMContentLoaded', () => {
    // Initialize global variables
    const newNoteBtn = document.getElementById('newNote');
    const saveNoteBtn = document.getElementById('saveNote');
    const downloadTxtBtn = document.getElementById('downloadTxt');
    noteTitle = document.getElementById('noteTitle');
    noteContent = document.getElementById('noteContent');
    notesList = document.getElementById('notesList');
    journalDate = document.getElementById('journalDate');

    let currentNoteId = null;

    // Fetch all notes
    const fetchNotes = async () => {
        const response = await fetch('/api/notes');
        const notes = await response.json();
        renderNotesList(notes);
    };

    // Render notes list with truncated content preview
    const renderNotesList = (notes) => {
        notesList.innerHTML = notes.map(note => {
            // Format the date manually without timezone conversion
            const dateStr = note.journal_date.split('T')[0];
            const [year, month, day] = dateStr.split('-');
            const date = `${month}/${day}/${year}`;
            
            const preview = note.content.substring(0, 50) + (note.content.length > 50 ? '...' : '');
            return `
                <div class="note-item" data-note-id="${note.id}">
                    <div class="note-info" onclick="loadNote(${note.id})">
                        <div class="note-header">
                            <span class="note-date">${date}</span>
                            <span class="mood-emoji">${note.mood_emoji}</span>
                        </div>
                        <div class="note-title">${note.title || 'Untitled'}</div>
                        <div class="note-preview">${preview}</div>
                    </div>
                    <button class="delete-btn" onclick="event.stopPropagation(); deleteNote(${note.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
        }).join('');
    };

    // Create new note
    newNoteBtn.addEventListener('click', () => {
        if (noteContent.value && !confirm('Are you sure you want to create a new note? Current note will be lost.')) {
            return;
        }
        currentNoteId = null;
        noteTitle.value = '';
        noteContent.value = '';
        journalDate.valueAsDate = new Date();
        document.querySelectorAll('.note-item').forEach(item => item.classList.remove('active'));
    });

    // Auto-save while typing (with debounce)
    let saveTimeout;
    const autoSave = () => {
        if (!noteContent.value) return;
        
        clearTimeout(saveTimeout);
        saveTimeout = setTimeout(() => saveNote(false), 1000); // Pass false to not show confirmation for auto-save
    };

    noteTitle.addEventListener('input', autoSave);
    noteContent.addEventListener('input', autoSave);

    // Handle keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Cmd/Ctrl + S to save
        if ((e.metaKey || e.ctrlKey) && e.key === 's') {
            e.preventDefault();
            saveNoteBtn.click();
        }
        // Cmd/Ctrl + N for new note
        if ((e.metaKey || e.ctrlKey) && e.key === 'n') {
            e.preventDefault();
            newNoteBtn.click();
        }
    });

    // Download as txt
    downloadTxtBtn.addEventListener('click', () => {
        if (!noteContent.value) {
            alert('Please write something before downloading!');
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

    // Save note
    const saveNote = async (showConfirmation = false) => {
        if (!noteContent.value) return;

        try {
            const noteData = {
                title: noteTitle.value,
                content: noteContent.value,
                journal_date: journalDate.value
            };

            const url = currentNoteId ? `/api/notes/${currentNoteId}` : '/api/notes';
            const method = currentNoteId ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(noteData)
            });

            if (!response.ok) {
                const contentType = response.headers.get("content-type");
                if (contentType && contentType.includes("application/json")) {
                    const errorData = await response.json();
                    throw new Error(errorData.message || 'Failed to save note');
                } else {
                    throw new Error('Server error: Failed to save note');
                }
            }

            const savedNote = await response.json();
            currentNoteId = savedNote.id;
            
            // Refresh the notes list
            await fetchNotes();
            
            if (showConfirmation) {
                const saveConfirm = document.createElement('div');
                saveConfirm.className = 'save-confirmation';
                saveConfirm.textContent = 'Saved!';
                document.body.appendChild(saveConfirm);
                
                setTimeout(() => {
                    saveConfirm.remove();
                }, 2000);
            }
        } catch (error) {
            console.error('Save failed:', error);
            alert(error.message);
        }
    };

    // Update the save button click handler
    saveNoteBtn.addEventListener('click', async () => {
        if (!noteContent.value) {
            alert('Please write something before saving!');
            return;
        }
        await saveNote(true); // Pass true to show save confirmation
    });

    // Set today's date as default
    journalDate.valueAsDate = new Date();

    // Initial load
    fetchNotes();
});

function displayNote(note) {
    try {
        currentNoteId = note.id;
        noteTitle.value = note.title || '';
        noteContent.value = note.content || '';
        
        // Handle the date without timezone conversion
        if (note.journal_date) {
            journalDate.value = note.journal_date.split('T')[0];
        } else {
            journalDate.valueAsDate = new Date();
        }
        
        // Update active state in sidebar
        document.querySelectorAll('.note-item').forEach(item => {
            item.classList.toggle('active', parseInt(item.dataset.noteId) === currentNoteId);
        });

        // Ensure the content is properly sized
        autoResizeTextarea(noteContent);
    } catch (error) {
        console.error('Error displaying note:', error);
        alert('Failed to display note. Please try again.');
    }
}

// Update the loadNote function to use displayNote
async function loadNote(noteId) {
    try {
        const response = await fetch(`/api/notes/${noteId}`);
        if (!response.ok) {
            throw new Error('Failed to load note');
        }
        const note = await response.json();
        displayNote(note);
    } catch (error) {
        console.error('Error loading note:', error);
        alert('Failed to load note. Please try again.');
    }
} 