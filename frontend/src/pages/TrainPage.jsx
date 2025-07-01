import React, { useState } from 'react';
import axios from 'axios';
import { UploadCloud, FileCheck, AlertTriangle, LoaderCircle, BrainCircuit } from 'lucide-react';

const TrainPage = () => {
  const [file, setFile] = useState(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [trainLoading, setTrainLoading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState({ text: '', type: '' });
  const [trainMessage, setTrainMessage] = useState({ text: '', type: '' });

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

  const handleFileChange = (e) => {
    setUploadMessage({ text: '', type: '' });
    setFile(e.target.files[0]);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      setUploadMessage({ text: 'Por favor, selecione um arquivo para o treinamento.', type: 'error' });
      return;
    }
    setUploadLoading(true);
    setUploadMessage({ text: '', type: '' });
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_URL}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setUploadMessage({ text: response.data.message || 'Arquivo processado com sucesso!', type: 'success' });
    } catch (error) {
      const errorMsg = error.response?.data?.error || 'Erro desconhecido ao processar o arquivo.';
      setUploadMessage({ text: errorMsg, type: 'error' });
    } finally {
      setUploadLoading(false);
      setFile(null);
      if (e.target) e.target.reset();
    }
  };

  const handleTrain = async () => {
    setTrainLoading(true);
    setTrainMessage({ text: '', type: '' });
    try {
      const response = await axios.post(`${API_URL}/train`);
      const { message, accuracy } = response.data;
      const successMsg = `${message} Acurácia do modelo: ${(accuracy * 100).toFixed(2)}%`;
      setTrainMessage({ text: successMsg, type: 'success' });
    } catch (error) {
      const errorMsg = error.response?.data?.error || 'Erro desconhecido ao treinar o modelo.';
      setTrainMessage({ text: errorMsg, type: 'error' });
    } finally {
      setTrainLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Card de Upload */}
      <div className="bg-white dark:bg-slate-800 p-8 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700">
        <div className="flex items-center text-blue-500 dark:text-blue-400 mb-4">
          <UploadCloud size={32} className="mr-3" />
          <h2 className="text-2xl font-bold">1. Enviar Dados para Treinamento</h2>
        </div>
        <p className="text-slate-600 dark:text-slate-400 mb-6">
          Envie relatórios de desvio nos formatos <code>.docx</code>, <code>.pdf</code>, ou um arquivo <code>.zip</code> contendo múltiplos documentos para alimentar a base de conhecimento.
        </p>
        <form onSubmit={handleUpload}>
          <div className="border-2 border-dashed border-slate-300 dark:border-slate-600 rounded-xl p-6 text-center mb-4 cursor-pointer hover:border-blue-500 dark:hover:border-blue-400 transition-colors">
            <input
              type="file"
              id="file-upload"
              onChange={handleFileChange}
              className="hidden"
              accept=".docx,.pdf,.zip"
              disabled={uploadLoading}
            />
            <label htmlFor="file-upload" className="cursor-pointer">
              <UploadCloud className="mx-auto h-12 w-12 text-slate-400" />
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
                {file ? `Arquivo selecionado: ${file.name}` : 'Arraste e solte ou clique para selecionar o arquivo'}
              </p>
            </label>
          </div>
          <button type="submit" disabled={uploadLoading || !file} className="w-full flex justify-center items-center bg-blue-600 text-white font-bold py-3 px-4 rounded-lg hover:bg-blue-700 transition duration-300 disabled:bg-blue-300 dark:disabled:bg-slate-600">
            {uploadLoading ? <><LoaderCircle className="animate-spin mr-2" /> Processando...</> : 'Enviar Arquivo'}
          </button>
        </form>
        {uploadMessage.text && (
          <div className={`mt-6 p-4 rounded-lg flex items-center text-sm ${uploadMessage.type === 'success' ? 'bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-300' : 'bg-red-100 dark:bg-red-900/50 text-red-800 dark:text-red-300'}`}>
            {uploadMessage.type === 'success' ? <FileCheck className="mr-3" /> : <AlertTriangle className="mr-3" />}
            {uploadMessage.text}
          </div>
        )}
      </div>
    </div>
  );
};

export default TrainPage;