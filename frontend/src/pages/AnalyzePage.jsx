import React, { useState } from 'react';
import axios from 'axios';
import { BrainCircuit, Lightbulb, LoaderCircle } from 'lucide-react';

const AnalyzePage = () => {
    const [description, setDescription] = useState('');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const API_URL = 'http://localhost:8000/api';

    const handleAnalyze = async (e) => {
        e.preventDefault();
        if (!description) {
            setError('Por favor, insira uma descrição para análise.');
            return;
        }
        setLoading(true);
        setResult(null);
        setError('');

        try {
            const response = await axios.post(`${API_URL}/analyze`, { description });
            setResult(response.data);
        } catch (err) {
            const errorMsg = err.response?.data?.error || 'Erro desconhecido ao realizar a análise.';
            setError(errorMsg);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <div className="bg-white dark:bg-slate-800 p-8 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700 mb-8">
                <div className="flex items-center text-blue-500 dark:text-blue-400 mb-4">
                    <BrainCircuit size={32} className="mr-3" />
                    <h2 className="text-2xl font-bold">Análise Preditiva</h2>
                </div>
                <p className="text-slate-600 dark:text-slate-400 mb-6">
                    Insira a descrição de um novo desvio. A IA irá analisar o texto e prever a causa raiz mais provável com base nos dados históricos de treinamento.
                </p>
                <form onSubmit={handleAnalyze}>
                    <textarea
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        rows="5"
                        className="w-full p-3 bg-slate-50 dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
                        placeholder="Ex: Durante o processo de envase do lote X, foi observada uma variação na coloração do produto..."
                    ></textarea>
                    <button type="submit" disabled={loading} className="w-full flex justify-center items-center bg-blue-600 text-white font-bold py-3 px-4 rounded-lg hover:bg-blue-700 transition duration-300 disabled:bg-blue-300 dark:disabled:bg-slate-600">
                        {loading ? <><LoaderCircle className="animate-spin mr-2" /> Analisando...</> : 'Analisar Causa Raiz'}
                    </button>
                </form>
                {error && (
                    <p className="mt-4 text-sm text-red-600 dark:text-red-400">{error}</p>
                )}
            </div>

            {result && (
                <div className="bg-white dark:bg-slate-800 p-8 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700 animate-fade-in">
                    <div className="flex items-center text-green-500 dark:text-green-400 mb-4">
                        <Lightbulb size={32} className="mr-3" />
                        <h3 className="text-2xl font-bold">Resultado da Análise</h3>
                    </div>
                    <div className="bg-slate-50 dark:bg-slate-700/50 p-6 rounded-lg space-y-4">
                        <div>
                            <h4 className="font-semibold text-slate-600 dark:text-slate-300">Descrição Analisada:</h4>
                            <p className="text-slate-800 dark:text-slate-200 italic">"{result.description}"</p>
                        </div>
                        <div className="border-t border-slate-200 dark:border-slate-600 my-4"></div>
                        <div>
                            <h4 className="font-semibold text-slate-600 dark:text-slate-300">Causa Raiz Prevista:</h4>
                            <p className="text-blue-600 dark:text-blue-400 font-bold text-xl">{result.prediction}</p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AnalyzePage;