import React, { useState } from 'react';
import axios from 'axios';
import { UploadCloud, FileCheck, AlertTriangle, LoaderCircle } from 'lucide-react';

const TrainPage = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

  const handleFileChange = (e) => {
    setMessage({ text: '', type: '' });
    setFile(e.target.files[0]);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      setMessage({ text: 'Por favor, selecione um arquivo para o treinamento.', type: 'error' });
      return;
    }
    setLoading(true);
    setMessage({ text: '', type: '' });
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_URL}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setMessage({ text: response.data.message || 'Arquivo processado com sucesso!', type: 'success' });
    } catch (error) {
      const errorMsg = error.response?.data?.error || 'Erro desconhecido ao processar o arquivo.';
      setMessage({ text: errorMsg, type: 'error' });
    } finally {
      setLoading(false);
      setFile(null);
      if (e.target) e.target.reset();
    }
  };

  return (
    <div>
        <div className="bg-white dark:bg-slate-800 p-8 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700">
          <div className="flex items-center text-blue-500 dark:text-blue-400 mb-4">
              <UploadCloud size={32} className="mr-3" />
              <h2 className="text-2xl font-bold">Treinamento do Modelo</h2>
          </div>
          <p className="text-slate-600 dark:text-slate-400 mb-6">
            Envie relatórios de desvio nos formatos <code>.docx</code>, <code>.pdf</code>, ou um arquivo <code>.zip</code> contendo múltiplos documentos.
            O sistema irá extrair os dados, adicioná-los ao banco e retreinar o modelo de IA.
          </p>
          <form onSubmit={handleUpload}>
            <div className="border-2 border-dashed border-slate-300 dark:border-slate-600 rounded-xl p-6 text-center mb-4 cursor-pointer hover:border-blue-500 dark:hover:border-blue-400 transition-colors">
                <input
                    type="file"
                    id="file-upload"
                    onChange={handleFileChange}
                    className="hidden"
                    accept=".docx,.pdf,.zip"
                    disabled={loading}
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                    <UploadCloud className="mx-auto h-12 w-12 text-slate-400" />
                    <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
                        {file ? `Arquivo selecionado: ${file.name}` : 'Arraste e solte ou clique para selecionar o arquivo'}
                    </p>
                </label>
            </div>
            <button type="submit" disabled={loading || !file} className="w-full flex justify-center items-center bg-blue-600 text-white font-bold py-3 px-4 rounded-lg hover:bg-blue-700 transition duration-300 disabled:bg-blue-300 dark:disabled:bg-slate-600">
                {loading ? <><LoaderCircle className="animate-spin mr-2" /> Processando...</> : 'Enviar e Processar'}
            </button>
          </form>
          {message.text && (
            <div className={`mt-6 p-4 rounded-lg flex items-center text-sm ${message.type === 'success' ? 'bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-300' : 'bg-red-100 dark:bg-red-900/50 text-red-800 dark:text-red-300'}`}>
                {message.type === 'success' ? <FileCheck className="mr-3" /> : <AlertTriangle className="mr-3" />}
                {message.text}
            </div>
          )}
        </div>
    </div>
  );
};

export default TrainPage;