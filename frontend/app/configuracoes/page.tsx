'use client';

import { useState } from 'react';
import Image from 'next/image';
import { 
  Home, 
  Grid, 
  BarChart2, 
  History, 
  Settings, 
  Bell, 
  LogOut,
  ChevronDown,
  X,
  FileText,
  Info,
  HelpCircle,
  Moon,
  Trash2,
  Plus,
  Minus,
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  ShieldCheck
} from 'lucide-react';
import Link from 'next/link';

export default function Configuracoes() {
  const [temNotificacoes, setTemNotificacoes] = useState(true);
  const [showNotificationsModal, setShowNotificationsModal] = useState(false);
  const [notificacoesAtivas, setNotificacoesAtivas] = useState(true);
  const [modoEscuro, setModoEscuro] = useState(false);
  const [tamanhoFonte, setTamanhoFonte] = useState(10);

  // MODAIS DE INFORMAÇÕES
  const [modalConteudo, setModalConteudo] = useState<{
    titulo: string;
    subtitulo: string;
    texto: string;
    icone: any;
  } | null>(null);

  // MODAL EXCLUIR CONTA
  const [showExcluirContaModal, setShowExcluirContaModal] = useState(false);

  // FEEDBACK
  const [feedback, setFeedback] = useState<{
    tipo: 'sucesso' | 'erro' | 'atencao' | null;
    titulo: string;
    mensagem: string;
  }>({ tipo: null, titulo: '', mensagem: '' });

  const aumentarFonte = () => setTamanhoFonte((prev) => Math.min(prev + 1, 20));
  const diminuirFonte = () => setTamanhoFonte((prev) => Math.max(prev - 1, 8));

  const handleExcluirConta = () => {
    setShowExcluirContaModal(false);
    setFeedback({
      tipo: 'erro',
      titulo: 'Solicitação Enviada',
      mensagem: 'Sua solicitação de exclusão de conta foi processada com sucesso.'
    });
  };

  return (
    <div className={`min-h-screen ${modoEscuro ? 'bg-slate-900 text-slate-100' : 'bg-[#F8FAFC] text-slate-800'} flex font-sans relative transition-colors duration-200`}>
      
      {/* SIDEBAR LATERAL */}
      <aside className={`w-64 ${modoEscuro ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-100'} border-r p-6 flex flex-col justify-between min-h-screen shadow-sm shrink-0`}>
        <div className="flex flex-col gap-8">
          
          <div className="flex justify-center w-full px-2">
            <div className="relative w-24 h-24 flex items-center justify-center shrink-0">
              <Image 
                src="/logo.png" 
                alt="Logo C.A.S.A" 
                width={96} 
                height={96} 
                className="object-contain"
                priority 
              />
            </div>
          </div>

          <nav className="flex flex-col gap-2">
            <Link 
              href="/dashboard"
              className={`flex items-center gap-3 px-4 py-3 rounded-2xl ${modoEscuro ? 'text-slate-400 hover:bg-slate-700 hover:text-[#5F7DE3]' : 'text-slate-500 hover:bg-slate-50 hover:text-[#5F7DE3]'} font-medium text-sm transition-all cursor-pointer`}
            >
              <Home className="w-5 h-5" />
              Início
            </Link>

            <Link 
              href="/categoria"
              className={`flex items-center gap-3 px-4 py-3 rounded-2xl ${modoEscuro ? 'text-slate-400 hover:bg-slate-700 hover:text-[#5F7DE3]' : 'text-slate-500 hover:bg-slate-50 hover:text-[#5F7DE3]'} font-medium text-sm transition-all cursor-pointer`}
            >
              <Grid className="w-5 h-5" />
              Categorias
            </Link>

            <Link 
              href="/desempenho"
              className={`flex items-center gap-3 px-4 py-3 rounded-2xl ${modoEscuro ? 'text-slate-400 hover:bg-slate-700 hover:text-[#5F7DE3]' : 'text-slate-500 hover:bg-slate-50 hover:text-[#5F7DE3]'} font-medium text-sm transition-all cursor-pointer`}
            >
              <BarChart2 className="w-5 h-5" />
              Desempenho
            </Link>

            <Link 
              href="/historico"
              className={`flex items-center gap-3 px-4 py-3 rounded-2xl ${modoEscuro ? 'text-slate-400 hover:bg-slate-700 hover:text-[#5F7DE3]' : 'text-slate-500 hover:bg-slate-50 hover:text-[#5F7DE3]'} font-medium text-sm transition-all cursor-pointer`}
            >
              <History className="w-5 h-5" />
              Histórico
            </Link>

            <Link 
              href="/configuracoes"
              className="flex items-center gap-3 px-4 py-3 rounded-2xl bg-[#5F7DE3] text-white font-medium text-sm shadow-md shadow-[#5F7DE3]/25 transition-all cursor-pointer"
            >
              <Settings className="w-5 h-5" />
              Configurações
            </Link>
          </nav>
        </div>

        <div className={`flex flex-col gap-3 pt-6 border-t ${modoEscuro ? 'border-slate-700' : 'border-slate-100'}`}>
          <div className={`flex items-center justify-between p-2 rounded-2xl ${modoEscuro ? 'bg-slate-700 border-slate-600' : 'bg-slate-50 border-slate-100'} border`}>
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-[#5F7DE3] text-white flex items-center justify-center font-bold text-sm">
                Z
              </div>
              <span className={`font-semibold text-sm ${modoEscuro ? 'text-slate-200' : 'text-slate-700'}`}>Zeus Alves</span>
            </div>
            <ChevronDown className="w-4 h-4 text-slate-400" />
          </div>

          <Link href="/" className="w-full">
            <button className="flex items-center justify-center gap-2 w-full py-2.5 rounded-xl bg-slate-500 hover:bg-slate-600 text-white text-xs font-semibold transition-all shadow-sm cursor-pointer">
              <LogOut className="w-4 h-4" />
              Desconectar
            </button>
          </Link>
        </div>
      </aside>

      {/* CONTEÚDO PRINCIPAL */}
      <main className="flex-1 p-8 flex flex-col gap-6 max-w-5xl mx-auto relative">
        
        {/* BARRA SUPERIOR DE SIMULAÇÃO */}
        <div className={`flex justify-between items-center ${modoEscuro ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-100'} p-3.5 rounded-2xl border shadow-xs`}>
          <div className="flex items-center gap-3 text-xs text-slate-500">
            <span className={`font-bold ${modoEscuro ? 'text-slate-300' : 'text-slate-700'} flex items-center gap-1`}>
              <RefreshCw className="w-3.5 h-3.5 text-[#5F7DE3]" /> Simular Estado:
            </span>
            <button 
              onClick={() => setTemNotificacoes(!temNotificacoes)}
              className={`px-3 py-1 rounded-lg text-[11px] font-semibold transition-all cursor-pointer ${
                temNotificacoes ? 'bg-amber-100 text-amber-700' : 'bg-slate-100 text-slate-500'
              }`}
            >
              {temNotificacoes ? 'Com Notificações' : 'Sem Notificações'}
            </button>
          </div>

          <button 
            onClick={() => setShowNotificationsModal(!showNotificationsModal)}
            className={`p-2.5 rounded-2xl ${modoEscuro ? 'bg-slate-700 border-slate-600' : 'bg-slate-50 border-slate-100'} border text-[#5F7DE3] hover:opacity-80 transition-all shadow-xs relative cursor-pointer`}
          >
            <Bell className="w-5 h-5" />
            {temNotificacoes && (
              <span className="absolute top-2 right-2 w-2.5 h-2.5 rounded-full bg-amber-400 border-2 border-white"></span>
            )}
          </button>
        </div>

        <section 
          className="w-full h-28 rounded-3xl p-8 flex items-center justify-center text-white shadow-lg relative overflow-hidden text-center"
          style={{
            background: 'linear-gradient(90deg, #F5AC46 0%, #6586F3 52%, #4D66B8 88%, #3B4E8D 100%)'
          }}
        >
          <h1 className="text-3xl font-extrabold drop-shadow-sm">Configurações</h1>
        </section>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-2 items-start">
          
          {/* SEÇÃO SISTEMA */}
          <div className="flex flex-col gap-3">
            <h2 className={`text-center font-bold ${modoEscuro ? 'text-slate-300' : 'text-slate-600'} text-sm`}>Sistema</h2>

            <div className={`${modoEscuro ? 'bg-slate-800 border-slate-700' : 'bg-[#FAF8FC] border-purple-100/80'} border rounded-3xl p-6 flex flex-col gap-5 shadow-xs`}>
              
              <div className="flex flex-col gap-2">
                <span className="text-[11px] font-medium text-slate-400">Ativar/Desativar</span>
                <div className={`${modoEscuro ? 'bg-slate-700 border-slate-600' : 'bg-white/90 border-purple-100'} border rounded-2xl p-3.5 flex items-center justify-between shadow-xs`}>
                  <div className="flex items-center gap-3">
                    <Bell className={`w-4 h-4 ${modoEscuro ? 'text-slate-300' : 'text-slate-600'}`} />
                    <span className={`text-xs font-semibold ${modoEscuro ? 'text-slate-200' : 'text-slate-700'}`}>Notificações</span>
                  </div>
                  
                  <button 
                    onClick={() => setNotificacoesAtivas(!notificacoesAtivas)}
                    className={`w-11 h-6 flex items-center rounded-full p-1 cursor-pointer transition-colors ${
                      notificacoesAtivas ? 'bg-[#5F7DE3]' : 'bg-slate-300'
                    }`}
                  >
                    <div 
                      className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform ${
                        notificacoesAtivas ? 'translate-x-5' : 'translate-x-0'
                      }`}
                    />
                  </button>
                </div>
              </div>

              <div className="flex flex-col gap-2">
                <span className="text-[11px] font-medium text-slate-400">Termos e Regras</span>
                
                <div className="flex flex-col gap-2.5">
                  <button 
                    onClick={() => setModalConteudo({
                      titulo: 'Termos de Privacidade',
                      subtitulo: 'Segurança e Proteção de Dados',
                      texto: 'O projeto C.A.S.A respeita totalmente a sua privacidade. Todos os dados de uso dos botões e histórico de acionamentos são mantidos de forma segura e criptografada para o acompanhamento dos responsáveis e educadores.',
                      icone: ShieldCheck
                    })}
                    className={`${modoEscuro ? 'bg-slate-700 border-slate-600 hover:bg-slate-600' : 'bg-white/90 border-purple-100 hover:bg-slate-50'} border rounded-2xl p-3.5 flex items-center gap-3 shadow-xs transition-all cursor-pointer text-left`}
                  >
                    <FileText className={`w-4 h-4 ${modoEscuro ? 'text-slate-300' : 'text-slate-600'}`} />
                    <span className={`text-xs font-semibold ${modoEscuro ? 'text-slate-200' : 'text-slate-700'}`}>Termos de privacidade</span>
                  </button>

                  <button 
                    onClick={() => setModalConteudo({
                      titulo: 'Informações do Sistema',
                      subtitulo: 'Plataforma C.A.S.A v1.0',
                      texto: 'O C.A.S.A (Comunicação Alternativa e Suporte Assistivo) é uma plataforma desenvolvida para conectar dispositivos físicos baseados em microcontroladores ESP32 a pranchas de comunicação dinâmica para pessoas com necessidades especiais.',
                      icone: Info
                    })}
                    className={`${modoEscuro ? 'bg-slate-700 border-slate-600 hover:bg-slate-600' : 'bg-white/90 border-purple-100 hover:bg-slate-50'} border rounded-2xl p-3.5 flex items-center gap-3 shadow-xs transition-all cursor-pointer text-left`}
                  >
                    <Info className={`w-4 h-4 ${modoEscuro ? 'text-slate-300' : 'text-slate-600'}`} />
                    <span className={`text-xs font-semibold ${modoEscuro ? 'text-slate-200' : 'text-slate-700'}`}>Informações</span>
                  </button>

                  <button 
                    onClick={() => setModalConteudo({
                      titulo: 'Suporte Técnico',
                      subtitulo: 'Como podemos ajudar?',
                      texto: 'Precisa de ajuda com a sincronização do hardware ESP32 ou personalização das vozes? Entre em contato com nossa equipe de suporte através do e-mail suporte@projetocasa.org ou consulte nossos tutoriais.',
                      icone: HelpCircle
                    })}
                    className={`${modoEscuro ? 'bg-slate-700 border-slate-600 hover:bg-slate-600' : 'bg-white/90 border-purple-100 hover:bg-slate-50'} border rounded-2xl p-3.5 flex items-center gap-3 shadow-xs transition-all cursor-pointer text-left`}
                  >
                    <HelpCircle className={`w-4 h-4 ${modoEscuro ? 'text-slate-300' : 'text-slate-600'}`} />
                    <span className={`text-xs font-semibold ${modoEscuro ? 'text-slate-200' : 'text-slate-700'}`}>Suporte</span>
                  </button>
                </div>
              </div>

            </div>
          </div>

          {/* SEÇÃO ACESSIBILIDADE E CONTA */}
          <div className="flex flex-col gap-6">
            
            <div className="flex flex-col gap-3">
              <h2 className={`text-center font-bold ${modoEscuro ? 'text-slate-300' : 'text-slate-600'} text-sm`}>Acessibilidade</h2>

              <div className={`${modoEscuro ? 'bg-slate-800 border-slate-700' : 'bg-[#FAF8FC] border-purple-100/80'} border rounded-3xl p-6 flex flex-col gap-5 shadow-xs`}>
                
                <div className="flex flex-col gap-2">
                  <span className="text-[11px] font-medium text-slate-400">Modo Claro/Escuro</span>
                  <div className={`${modoEscuro ? 'bg-slate-700 border-slate-600' : 'bg-white/90 border-purple-100'} border rounded-2xl p-3.5 flex items-center justify-between shadow-xs`}>
                    <div className="flex items-center gap-3">
                      <Moon className={`w-4 h-4 ${modoEscuro ? 'text-slate-300' : 'text-slate-600'}`} />
                      <span className={`text-xs font-semibold ${modoEscuro ? 'text-slate-200' : 'text-slate-700'}`}>Modo Escuro</span>
                    </div>

                    <button 
                      onClick={() => setModoEscuro(!modoEscuro)}
                      className={`w-11 h-6 flex items-center rounded-full p-1 cursor-pointer transition-colors ${
                        modoEscuro ? 'bg-[#5F7DE3]' : 'bg-slate-300'
                      }`}
                    >
                      <div 
                        className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform ${
                          modoEscuro ? 'translate-x-5' : 'translate-x-0'
                        }`}
                      />
                    </button>
                  </div>
                </div>

                <div className="flex flex-col gap-2">
                  <span className="text-[11px] font-medium text-slate-400">Tamanho da Fonte</span>
                  <div className={`${modoEscuro ? 'bg-slate-700 border-slate-600' : 'bg-white/90 border-purple-100'} border rounded-2xl p-3.5 flex items-center justify-between shadow-xs`}>
                    <span className={`font-extrabold ${modoEscuro ? 'text-slate-200' : 'text-slate-700'} text-sm`}>Tt</span>

                    <div className="flex items-center gap-2">
                      <button 
                        onClick={aumentarFonte}
                        className="w-7 h-7 rounded-lg bg-slate-200/80 hover:bg-slate-300 flex items-center justify-center text-slate-600 text-xs font-bold transition-colors cursor-pointer"
                      >
                        <Plus className="w-3.5 h-3.5" />
                      </button>

                      <span className="text-xs font-medium text-slate-400 px-3 py-1 bg-slate-50 border border-slate-100 rounded-md min-w-12 text-center">
                        {tamanhoFonte}px
                      </span>

                      <button 
                        onClick={diminuirFonte}
                        className="w-7 h-7 rounded-lg bg-slate-200/80 hover:bg-slate-300 flex items-center justify-center text-slate-600 text-xs font-bold transition-colors cursor-pointer"
                      >
                        <Minus className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                </div>

              </div>
            </div>

            <div className="flex flex-col gap-3">
              <h2 className={`text-center font-bold ${modoEscuro ? 'text-slate-300' : 'text-slate-600'} text-sm`}>Conta</h2>

              <div className={`${modoEscuro ? 'bg-slate-800 border-slate-700' : 'bg-[#FAF8FC] border-purple-100/80'} border rounded-3xl p-6 shadow-xs`}>
                <button 
                  onClick={() => setShowExcluirContaModal(true)}
                  className="w-full bg-white/90 border border-rose-100/80 rounded-2xl p-3.5 flex items-center justify-center gap-2 text-rose-500 hover:bg-rose-50 transition-all cursor-pointer shadow-xs"
                >
                  <Trash2 className="w-4 h-4 text-rose-600" />
                  <span className="text-xs font-semibold text-rose-600">Excluir conta</span>
                </button>
              </div>
            </div>

          </div>

        </div>

        {/* POP-UP DE NOTIFICAÇÕES */}
        {showNotificationsModal && (
          <div className="absolute top-20 right-8 w-80 bg-[#F3EFF5] rounded-3xl p-6 shadow-2xl border border-indigo-100 z-50 animate-in fade-in zoom-in duration-200">
            <div className="flex justify-between items-center mb-6">
              <h4 className="text-lg font-bold text-[#5F7DE3]">Notificações</h4>
              <button 
                onClick={() => setShowNotificationsModal(false)}
                className="text-slate-400 hover:text-slate-600 transition-colors p-1 cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {temNotificacoes ? (
              <div className="flex flex-col gap-3">
                <div className="bg-white p-3.5 rounded-2xl shadow-xs flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-400 to-purple-400 shrink-0 flex items-center justify-center text-white text-xs font-bold">
                      ESP
                    </div>
                    <div className="flex flex-col">
                      <span className="text-xs font-semibold text-slate-800">Dispositivo Conectado</span>
                      <span className="text-[10px] text-slate-400">ESP32 operando normalmente</span>
                    </div>
                  </div>
                  <span className="text-[10px] text-purple-500 font-medium">Agora</span>
                </div>
              </div>
            ) : (
              <div className="bg-white/60 border border-slate-200/60 p-6 rounded-2xl text-center flex flex-col items-center gap-2">
                <Bell className="w-8 h-8 text-slate-300" />
                <span className="text-xs text-slate-500 font-medium">Nenhuma notificação por enquanto.</span>
              </div>
            )}

            <div className="text-center mt-6">
              <button 
                onClick={() => setShowNotificationsModal(false)}
                className="text-xs text-slate-400 hover:text-slate-600 transition-colors cursor-pointer"
              >
                Fechar
              </button>
            </div>
          </div>
        )}

      </main>

      {/* MODAL INFORMATIVO (TERMOS / INFORMAÇÕES / SUPORTE) */}
      {modalConteudo && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center z-50 p-4 animate-in fade-in duration-200">
          <div className="bg-white w-full max-w-md rounded-3xl p-6 sm:p-8 shadow-2xl border border-slate-100 relative flex flex-col gap-4 text-center items-center">
            
            <button 
              onClick={() => setModalConteudo(null)}
              className="absolute top-6 right-6 text-slate-400 hover:text-slate-600 transition-colors p-1 cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="w-14 h-14 rounded-2xl bg-[#5F7DE3]/10 text-[#5F7DE3] flex items-center justify-center shrink-0">
              <modalConteudo.icone className="w-7 h-7" />
            </div>

            <div className="flex flex-col gap-1">
              <h3 className="text-lg font-bold text-slate-800">{modalConteudo.titulo}</h3>
              <span className="text-xs text-[#5F7DE3] font-semibold">{modalConteudo.subtitulo}</span>
            </div>

            <p className="text-xs text-slate-500 leading-relaxed max-w-sm">
              {modalConteudo.texto}
            </p>

            <button 
              onClick={() => setModalConteudo(null)}
              className="w-full py-3.5 rounded-2xl bg-[#5F7DE3] hover:bg-[#4d6bd3] text-white font-semibold text-xs transition-all shadow-md shadow-[#5F7DE3]/20 cursor-pointer mt-2"
            >
              Entendido
            </button>

          </div>
        </div>
      )}

      {/* MODAL CONFIRMAÇÃO EXCLUIR CONTA */}
      {showExcluirContaModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center z-50 p-4 animate-in fade-in duration-200">
          <div className="bg-white w-full max-w-sm rounded-3xl p-6 shadow-2xl border border-slate-100 text-center flex flex-col items-center gap-4">
            
            <div className="w-14 h-14 rounded-full bg-rose-100 text-rose-600 flex items-center justify-center shadow-xs">
              <AlertTriangle className="w-7 h-7" />
            </div>

            <div className="flex flex-col gap-1">
              <h3 className="text-lg font-bold text-slate-800">Deseja excluir a conta?</h3>
              <p className="text-xs text-slate-500 leading-relaxed">
                Esta ação apagará permanentemente todas as suas categorias, botões personalizados e histórico de acionamentos.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-3 w-full mt-2">
              <button 
                onClick={() => setShowExcluirContaModal(false)}
                className="py-3 rounded-2xl bg-slate-100 hover:bg-slate-200 text-slate-600 font-semibold text-xs transition-all cursor-pointer"
              >
                Cancelar
              </button>

              <button 
                onClick={handleExcluirConta}
                className="py-3 rounded-2xl bg-rose-600 hover:bg-rose-700 text-white font-semibold text-xs transition-all shadow-md shadow-rose-600/20 cursor-pointer"
              >
                Sim, Excluir
              </button>
            </div>

          </div>
        </div>
      )}

      {/* MODAL FEEDBACK */}
      {feedback.tipo && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center z-50 p-4 animate-in fade-in duration-200">
          <div className="bg-white w-full max-w-sm rounded-3xl p-6 shadow-2xl border border-slate-100 text-center flex flex-col items-center gap-4">
            {feedback.tipo === 'sucesso' && <CheckCircle2 className="w-12 h-12 text-emerald-500" />}
            {feedback.tipo === 'erro' && <XCircle className="w-12 h-12 text-rose-500" />}
            {feedback.tipo === 'atencao' && <AlertTriangle className="w-12 h-12 text-amber-500" />}
            <div className="flex flex-col gap-1">
              <h3 className="text-lg font-bold text-slate-800">{feedback.titulo}</h3>
              <p className="text-xs text-slate-500">{feedback.mensagem}</p>
            </div>
            <button 
              onClick={() => setFeedback({ tipo: null, titulo: '', mensagem: '' })} 
              className="w-full py-3 rounded-2xl bg-[#5F7DE3] text-white font-semibold text-xs cursor-pointer"
            >
              OK
            </button>
          </div>
        </div>
      )}

    </div>
  );
}