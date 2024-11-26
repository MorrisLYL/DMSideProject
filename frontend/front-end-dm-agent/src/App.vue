<template>
  <div class="p-6 bg-gray-50 min-h-screen">
    <div
      v-if="notification.show"
      :class="notification.type === 'success' ? 'bg-green-500' : 'bg-red-500'"
      class="fixed top-5 left-1/2 transform -translate-x-1/2 bg-green-500 text-white py-2 px-4 rounded shadow-lg"
    >
      {{ notification.message }}
    </div>
    
    <div class="flex justify-end items-center mb-6">
      <div class="flex space-x-4">
        <button
          class="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
          @click="deleteSelectedFiles"
        >
          Delete
        </button>
        <button
          class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          @click="openUploadModal"
        >
          Upload a new PDF file
        </button>
      </div>
    </div>

    <table class="table-auto w-full bg-white shadow-md rounded-lg overflow-hidden">
      <thead>
        <tr class="bg-gray-100">
          <th class="p-4 text-left">ID</th>
          <th class="p-4 text-left">File Name</th>
          <th class="p-4 text-left">Uploaded At</th>
          <th class="p-4 text-left">File Type</th>
          <th class="p-4 text-left">Status</th>
          <th class="p-4 text-left">Preview</th>
          <th class="p-4 text-left">
            <input class="cursor-pointer" type="checkbox" @change="toggleAllCheckboxes" />
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="file in files"
          :key="file.id"
          class="hover:bg-gray-50 border-t"
        >
          <td class="p-4">{{ file.id }}</td>
          <td class="p-4">{{ file.file_name }}</td>
          <td class="p-4">{{ file.uploaded_at }}</td>
          <td class="p-4">{{ file.file_type }}</td>
          <td class="p-4">
            <span
              :class="{
                'text-red-500': file.status === 'Uploading' || file.status === 'Parsing',
                'text-green-500': file.status === 'Completed',
                'text-yellow-500': file.status === 'Failed',
              }"
            >
              {{ file.status }}
            </span>
          </td>
          <td class="p-4">
            <button
              class="text-blue-500 hover:underline disabled:text-gray-400 disabled:cursor-not-allowed"
              :disabled="file.status !== 'Completed'"
              @click="previewFile(file.id)"
            >
              Open new Tab
            </button>
          </td>
          <td class="p-4">
            <input
              type="checkbox"
              v-model="selectedFiles"
              :value="file.id"
              :disabled="file.status !== 'Completed' && file.status !== 'Failed'"
              class="cursor-pointer disabled:cursor-not-allowed"              
            />
          </td>
        </tr>
      </tbody>
    </table>

    <Modal
      v-if="showModal"
      :show="showModal"
      title="Upload a New PDF File"
      @cancel="closeModal"
      @save="uploadFile"
    >
      <input
        type="file"
        accept="application/pdf"
        @change="handleFileUpload"
        class="mb-4"
      />
    </Modal>
  </div>
</template>

<script>
import axios from "axios";
import Modal from "./components/ConfirmModal.vue";
import { createWebSocket } from './utils/websocket';

export default {
  components: { Modal },
  data() {
    return {
      files: [],
      selectedFiles: [],
      showModal: false,
      selectedFile: null,
      notification:{
        show: false,
        message: "",
        type: "success"
      },
      websocket: null
    };
  },
  methods: {
    async fetchFiles() {
      try {
        const response = await axios.get("http://127.0.0.1:8000/files");
        this.files = response.data;
      } catch (error) {
        console.error("Error fetching files:", error);
        this.showNotification("Failed to fetch files.", "error");
      }
    },
    showNotification(message, type= "success") {
      this.notification.message = message;
      this.notification.type = type;
      this.notification.show = true;

      setTimeout(() => {
        this.notification.show = false;
      }, 3000);
    },    
    toggleAllCheckboxes(event) {
      this.selectedFiles = event.target.checked
        ? this.files.filter(file => file.status === "Completed" || file.status === "Failed").map((file) => file.id)
        : [];
    },
    openUploadModal() {
      this.showModal = true;
    },
    closeModal() {
      this.showModal = false;
      this.selectedFile = null;
    },
    handleFileUpload(event) {
      this.selectedFile = event.target.files[0];
    },
    async uploadFile() {
      if (!this.selectedFile){
        this.showNotification("No file selected.", "error");
        return
      }
      
      const formData = new FormData();
      formData.append("file", this.selectedFile);
  
      try {
        const response = await axios.post(
          "http://127.0.0.1:8000/upload/",
          formData,
          { headers: { "Content-Type": "multipart/form-data" } }
        );
        
        const { file_id, uploaded_at } = response.data;
        const newFile = {
          id: file_id,
          file_name: this.selectedFile.name,
          uploaded_at: uploaded_at,
          file_type: "PDF",
          status: "..."
        };
        this.files.push(newFile);
        this.closeModal();
        this.showNotification(`File ID ${newFile.file_name} is being processed.`);
      } catch (error) {
        console.error("Error uploading file:", error);
        this.showNotification(`Failed to upload "${this.selectedFile.name}".`, "error");
      }
    },
    async previewFile(fileId) {
      try {
        const response = await axios.get(
          `http://127.0.0.1:8000/preview/${fileId}`
        );
        const blob = new Blob([response.data.text_content], {
          type: "text/plain;charset=utf-8",
        });
        const url = window.URL.createObjectURL(blob);
        window.open(url, "_blank");
      } catch (error) {
        console.error("Error previewing file:", error);
        this.showNotification(`Failed to preview file ID ${fileId}.`, "error");
      }
    },
    async deleteSelectedFiles() {
      if (this.selectedFiles.length === 0) {
        this.showNotification("No files selected for deletion.", "error");
        return
      }      
      const confirmDelete = confirm(
        `Are you sure you want to delete ${this.selectedFiles.length} file(s)?`
      );
      if (!confirmDelete) return;

      for (const fileId of this.selectedFiles) {
        const file = this.files.find((f) => f.id === fileId);
        if (!file || (file.status !== "Completed" && file.status !== "Failed")) {
          this.showNotification(`File ID ${fileId} cannot be deleted because its status is not 'Completed' or 'Failed'.`);
          continue
        }        

        try {
          const response = await axios.delete(`http://127.0.0.1:8000/delete/${fileId}`);
          if (response.status === 200 && response.data.message === "success") {
            this.showNotification(`File ID ${fileId} deleted successfully.`);
            this.files = this.files.filter(f => f.id !== fileId);
          }
        } catch (error) {
          console.error(`Error deleting file with ID ${fileId}:`, error);
          this.showNotification(`Failed to delete file ID ${fileId}.`, "error");
        }
      }

      this.selectedFiles = [];
      await this.fetchFiles();
    },
    setupWebSocket() {
      this.websocket = createWebSocket(
        (message) => this.onWebSocketMessage(message),
        this.onWebSocketOpen,
        this.onWebSocketClose,
        this.onWebSocketError
      );
    },
    onWebSocketMessage(message) {
      try {
        const parsedMessage = JSON.parse(message);
        console.log("WebSocket received:", parsedMessage);

        const { file_id, status } = parsedMessage;

        if (file_id && status) {
          const fileIndex = this.files.findIndex(
            (file) => file.id === file_id
          );
          if (fileIndex !== -1) {
            // Update the status of the existing file
            this.files[fileIndex].status = status
            if (status === "Completed" || status === "Failed") {
              const fileName = this.files[fileIndex].file_name;
              this.showNotification(`File "${fileName}" is ${status}.`, status === "Completed" ? "success" : "error");
              this.fetchFiles();
            }
          } else {
            console.warn(`Received status update for unknown file_id: ${file_id}`);
          }          
        } else {
          console.warn("Unknown WebSocket message format:", parsedMessage);
        }

      } catch (error) {
        console.error("Error parsing WebSocket message:", error);
      }
    },
    onWebSocketOpen() {
      console.log("WebSocket connection established.");
    },
    onWebSocketClose() {
      console.log("WebSocket connection closed.");
    },
    onWebSocketError(error) {
      console.error("WebSocket error:", error);
    },    
  },
  mounted() {
    this.fetchFiles();
    this.setupWebSocket();
  },
  beforeUnmount() {
    if (this.websocket) {
      this.websocket.close();
    }
  }  
};
</script>
