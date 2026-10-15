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
  Cpu, 
  Info, 
  Power, 
  LogOut,
  ChevronDown,
  X,
  Trash2,
  Share2,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  RefreshCw,
  Wifi,
  BatteryCharging
} from 'lucide-react';
import Link from 'next/link';

export default function Dashboard() {
  // ESTADOS DE INTERFACE E SIMULAÇÃO DE DADOS
  const [temDispositivos, setTemDispositivos] = useState(true);
  const [temNotificacoes, setTemNotificacoes] = useState(true);

  // CONTROLE DOS MODAIS
  const [showNotifications, setShowNotifications] = useState(false);
  const [showDevicesModal, setShowDevicesModal] = useState(false);
  const [showDeviceDetails, setShowDeviceDetails] = useState(false);
  
  // MODAL DE CONFIRMAÇÃO DE EXCLUSÃO
  const [itemParaExcluir, setItemParaExcluir] = useState<string | null>(null);

  // MODAIS DE FEEDBACK (SUCESSO, ERRO, ATENÇÃO)
  const [feedback, setFeedback] = useState<{
    tipo: 'sucesso' | 'erro' | 'atencao' | null;
    titulo: string;
    mensagem: string;
  }>({ tipo: null, titulo: '', mensagem: '' });

  // Funções de simulação de ações
  const handleConfirmarExclusao = () => {
    const item = itemParaExcluir;
    setItemParaExcluir(null);

    // Simula remoção de dispositivo
    if (item === 'ESP32') {
      setTemDispositivos(false);
      setShowDevicesModal(false);
      setFeedback({
        tipo: 'sucesso',
        titulo: 'Dispositivo Removido',
        mensagem: 'O dispositivo ESP32 foi desconectado com sucesso!'
      });
    } else {
      // Exemplo de simulação de erro no back-end
      setFeedback({
        tipo: 'erro',
        titulo: 'Falha na Operação',
        mensagem: 'Não foi possível excluir este item no momento. Tente novamente.'
      });
    }
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-slate-800 flex font-sans relative">
      
      {/* 1. SIDEBAR LATERAL */}
      <aside className="w-64 bg-white border-r border-slate-100 p-6 flex flex-col justify-between min-h-screen shadow-sm shrink-0">
        <div className="flex flex-col gap-8">
          
          {/* Logo C.A.S.A */}
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

          {/* Menu de Navegação */}
          <nav className="flex flex-col gap-2">
            <Link 
              href="/dashboard"
              className="flex items-center gap-3 px-4 py-3 rounded-2xl bg-[#5F7DE3] text-white font-medium text-sm shadow-md shadow-[#5F7DE3]/25 transition-all cursor-pointer"
            >
              <Home className="w-5 h-5" />
              Início
            </Link>

            <Link 
              href="/categoria"
              className="flex items-center gap-3 px-4 py-3 rounded-2xl text-slate-500 hover:bg-slate-50 hover:text-[#5F7DE3] font-medium text-sm transition-all cursor-pointer"
            >
              <Grid className="w-5 h-5" />
              Categorias
            </Link>

            <Link 
              href="/desempenho"
              className="flex items-center gap-3 px-4 py-3 rounded-2xl text-slate-500 hover:bg-slate-50 hover:text-[#5F7DE3] font-medium text-sm transition-all cursor-pointer"
            >
              <BarChart2 className="w-5 h-5" />
              Desempenho
            </Link>

            <Link 
              href="/historico"
              className="flex items-center gap-3 px-4 py-3 rounded-2xl text-slate-500 hover:bg-slate-50 hover:text-[#5F7DE3] font-medium text-sm transition-all cursor-pointer"
            >
              <History className="w-5 h-5" />
              Histórico
            </Link>

            <Link 
              href="/configuracoes"
              className="flex items-center gap-3 px-4 py-3 rounded-2xl text-slate-500 hover:bg-slate-50 hover:text-[#5F7DE3] font-medium text-sm transition-all cursor-pointer"
            >
              <Settings className="w-5 h-5" />
              Configurações
            </Link>
          </nav>
        </div>

        {/* Perfil & Desconectar */}
        <div className="flex flex-col gap-3 pt-6 border-t border-slate-100">
          <div className="flex items-center justify-between p-2 rounded-2xl bg-slate-50 border border-slate-100">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-[#5F7DE3] text-white flex items-center justify-center font-bold text-sm">
                Z
              </div>
              <span className="font-semibold text-sm text-slate-700">Zeus Alves</span>
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

      {/* CONTEÚDO PRINCIPAL DA DASHBOARD */}
      <main className="flex-1 p-8 flex flex-col gap-8 max-w-6xl mx-auto relative">
        
        {/* BARRA SUPERIOR: CONTROLE DE SIMULAÇÃO + NOTIFICAÇÕES (Sem botão voltar redundante) */}
        <div className="flex justify-between items-center bg-white p-3.5 rounded-2xl border border-slate-100 shadow-xs">
          
          {/* Simulador de Estados (Para testes de Front/Back) */}
          <div className="flex items-center gap-3 text-xs text-slate-500">
            <span className="font-bold text-slate-700 flex items-center gap-1">
              <RefreshCw className="w-3.5 h-3.5 text-[#5F7DE3]" /> Simular Banco:
            </span>
            <button 
              onClick={() => setTemDispositivos(!temDispositivos)}
              className={`px-3 py-1 rounded-lg text-[11px] font-semibold transition-all cursor-pointer ${
                temDispositivos ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-500'
              }`}
            >
              {temDispositivos ? 'Com Dispositivo' : 'Sem Dispositivo'}
            </button>
            <button 
              onClick={() => setTemNotificacoes(!temNotificacoes)}
              className={`px-3 py-1 rounded-lg text-[11px] font-semibold transition-all cursor-pointer ${
                temNotificacoes ? 'bg-amber-100 text-amber-700' : 'bg-slate-100 text-slate-500'
              }`}
            >
              {temNotificacoes ? 'Com Notificações' : 'Sem Notificações'}
            </button>
          </div>

          {/* Botão de Notificação */}
          <button 
            onClick={() => setShowNotifications(!showNotifications)}
            className="p-2.5 rounded-2xl bg-slate-50 border border-slate-100 text-[#5F7DE3] hover:bg-slate-100 transition-all shadow-xs relative cursor-pointer"
            title="Notificações"
          >
            <Bell className="w-5 h-5" />
            {temNotificacoes && (
              <span className="absolute top-2 right-2 w-2.5 h-2.5 rounded-full bg-amber-400 border-2 border-white"></span>
            )}
          </button>
        </div>

        {/* HERO BANNER */}
        <section 
          className="w-full h-44 rounded-3xl p-8 flex flex-col justify-center text-white shadow-lg relative overflow-hidden"
          style={{
            background: 'linear-gradient(90deg, #F5AC46 0%, #6586F3 52%, #4D66B8 88%, #3B4E8D 100%)'
          }}
        >
          <h1 className="text-3xl font-extrabold mb-2 drop-shadow-sm">Olá, Zeus!</h1>
          <p className="text-white/90 font-normal text-sm max-w-md drop-shadow-sm">
            Personalize o seu dispositivo C.A.S.A ao seu estilo e acompanhe tudo em tempo real.
          </p>
        </section>

        {/* VISÃO GERAL */}
        <section className="flex flex-col gap-4">
          <h2 className="text-center font-bold text-slate-700 text-lg">Visão Geral</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            
            {/* CARD 1: Dispositivos Conectados */}
            <div className="bg-white border border-slate-100 rounded-3xl p-6 shadow-sm flex flex-col items-center text-center justify-between gap-4">
              <div className="flex items-center gap-2 text-slate-600 font-semibold text-xs">
                <Cpu className="w-4 h-4 text-slate-400" />
                Dispositivos Conectados
              </div>

              {temDispositivos ? (
                <div className="flex flex-col items-center gap-1 my-2">
                  <div className="flex items-center gap-2 text-xs text-slate-700 font-bold">
                    <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                    ESP32 (C.A.S.A. Main)
                  </div>
                  <span className="text-[11px] text-slate-400">Conectado e Operacional</span>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-1 my-2 py-1">
                  <span className="text-xs text-rose-500 font-medium">Nenhum dispositivo encontrado</span>
                  <span className="text-[10px] text-slate-400">Ligue o ESP32 para conectar</span>
                </div>
              )}

              <button 
                onClick={() => setShowDevicesModal(true)}
                className="w-full py-2.5 rounded-xl bg-[#5F7DE3] hover:bg-[#4d6bd3] text-white text-xs font-semibold transition-all shadow-sm cursor-pointer"
              >
                Gerenciar Dispositivos
              </button>
            </div>

            {/* CARD 2: Informações Gerais */}
            <div className="bg-white border border-slate-100 rounded-3xl p-6 shadow-sm flex flex-col items-center text-center justify-between gap-4">
              <div className="flex items-center gap-2 text-slate-600 font-semibold text-xs">
                <Info className="w-4 h-4 text-slate-400" />
                Status da Conexão
              </div>

              {temDispositivos ? (
                <div className="flex flex-col items-center gap-1 my-2">
                  <span className="text-xs text-slate-700 font-bold">Sinal 100% (Wi-Fi)</span>
                  <span className="text-[11px] text-slate-400">Rede: residencia_casa_2G</span>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-1 my-2 py-1">
                  <span className="text-xs text-slate-400 font-medium">Desconectado da nuvem</span>
                  <span className="text-[10px] text-slate-400">Aguardando pareamento</span>
                </div>
              )}

              <button 
                onClick={() => {
                  if (temDispositivos) {
                    setShowDeviceDetails(true);
                  } else {
                    setFeedback({
                      tipo: 'atencao',
                      titulo: 'Sem Conexão',
                      mensagem: 'Nenhum dispositivo está conectado para exibir estatísticas no momento.'
                    });
                  }
                }}
                className="w-full py-2.5 rounded-xl bg-[#5F7DE3] hover:bg-[#4d6bd3] text-white text-xs font-semibold transition-all shadow-sm cursor-pointer"
              >
                Mais Detalhes
              </button>
            </div>

            {/* CARD 3: Último Acionamento */}
            <div className="bg-white border border-slate-100 rounded-3xl p-6 shadow-sm flex flex-col items-center text-center justify-between gap-4">
              <div className="flex items-center gap-2 text-slate-600 font-semibold text-xs">
                <Power className="w-4 h-4 text-slate-400" />
                Último Acionamento
              </div>

              {temDispositivos ? (
                <div className="flex flex-col items-center gap-1 my-2">
                  <span className="text-xs text-slate-700 font-bold">Botão 2: Beber Água</span>
                  <span className="text-[11px] text-slate-400">Hoje às 20:30</span>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-1 my-2 py-1">
                  <span className="text-xs text-slate-400 font-medium">Sem registros recentes</span>
                  <span className="text-[10px] text-slate-400">Aguardando uso do botão</span>
                </div>
              )}

              <Link href="/historico" className="w-full">
                <button className="w-full py-2.5 rounded-xl bg-[#5F7DE3] hover:bg-[#4d6bd3] text-white text-xs font-semibold transition-all shadow-sm cursor-pointer">
                  Ver Histórico
                </button>
              </Link>
            </div>

          </div>
        </section>

        {/* FEEDBACK DE SUGESTÕES DA IA/SISTEMA */}
        <section className="flex flex-col gap-3 mt-2">
          <h3 className="font-bold text-slate-700 text-sm">Feedback de Atendimento:</h3>
          <div className="w-full bg-slate-100/70 border border-slate-200/60 rounded-3xl p-6 flex flex-col gap-2 text-xs text-slate-600">
            <p><strong className="text-slate-800">OBS:</strong> O botão menos utilizado nos últimos 7 dias é &quot;Música&quot; da categoria Escola.</p>
            <p><strong className="text-slate-800">Último uso registrado:</strong> 20/08/2026 - 17:00</p>
            <p><strong className="text-slate-800">Sugestão:</strong> Substitua este ícone por uma rotina de maior relevância, como &quot;Banheiro&quot; ou &quot;Lanche&quot;.</p>
          </div>
        </section>

        {/* MODAL DE NOTIFICAÇÕES (COM / SEM DADOS) */}
        {showNotifications && (
          <div className="absolute top-20 right-8 w-80 bg-[#F3EFF5] rounded-3xl p-6 shadow-2xl border border-indigo-100 z-50 animate-in fade-in zoom-in duration-200">
            <div className="flex justify-between items-center mb-6">
              <h4 className="text-lg font-bold text-[#5F7DE3]">Notificações</h4>
              <button 
                onClick={() => setShowNotifications(false)}
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
                      <span className="text-[10px] text-slate-400">ESP32 pareado com sucesso</span>
                    </div>
                  </div>
                  <span className="text-[10px] text-purple-500 font-medium">Agora</span>
                </div>

                <div className="bg-white p-3.5 rounded-2xl shadow-xs flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-amber-100 text-amber-600 shrink-0 flex items-center justify-center font-bold text-xs">
                      !
                    </div>
                    <div className="flex flex-col">
                      <span className="text-xs font-semibold text-slate-800">Bateria do ESP32</span>
                      <span className="text-[10px] text-slate-400">Nível em 100%</span>
                    </div>
                  </div>
                  <span className="text-[10px] text-slate-400 font-medium">10m</span>
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
                onClick={() => setShowNotifications(false)}
                className="text-xs text-slate-400 hover:text-slate-600 transition-colors cursor-pointer"
              >
                Fechar
              </button>
            </div>
          </div>
        )}
      </main>

      {/* ------------------- MODAIS DO SISTEMA ------------------- */}

      {/* MODAL 1: LISTA / GERENCIAR DISPOSITIVOS */}
      {showDevicesModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center z-50 p-4 animate-in fade-in duration-200">
          <div className="bg-[#F3EFF5] w-full max-w-md rounded-3xl p-6 shadow-2xl border border-indigo-100 relative flex flex-col items-center text-center">
            
            <button 
              onClick={() => setShowDevicesModal(false)}
              className="absolute top-5 right-5 text-slate-400 hover:text-slate-600 transition-colors p-1 cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-2 mb-2 mt-2">
              <Share2 className="w-6 h-6 text-[#5F7DE3]" />
              <h3 className="text-xl font-bold text-[#5F7DE3]">
                Dispositivos <span className="text-amber-500">Conectados</span>
              </h3>
            </div>

            <p className="text-xs text-slate-500 max-w-xs mb-6 leading-relaxed">
              Gerencie os dispositivos físicos que estão pareados com a sua conta.
            </p>

            {temDispositivos ? (
              <div className="w-full bg-white/80 border border-purple-200/80 rounded-2xl p-3.5 flex items-center justify-between mb-6 shadow-xs">
                <div className="flex items-center gap-3">
                  <span className="w-3 h-3 rounded-full bg-emerald-500 shadow-xs"></span>
                  <div className="flex flex-col text-left">
                    <span className="text-sm font-semibold text-slate-800">ESP32 - C.A.S.A.</span>
                    <span className="text-[10px] text-slate-400">ID: #ESP32-8829</span>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button 
                    onClick={() => {
                      setShowDevicesModal(false);
                      setShowDeviceDetails(true);
                    }}
                    className="p-1.5 text-slate-400 hover:text-[#5F7DE3] transition-colors cursor-pointer"
                    title="Ver detalhes do card"
                  >
                    <Info className="w-4 h-4" />
                  </button>

                  <button 
                    onClick={() => setItemParaExcluir('ESP32')}
                    className="p-1.5 text-rose-500 hover:text-rose-700 transition-colors cursor-pointer"
                    title="Excluir dispositivo"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ) : (
              <div className="w-full bg-white/60 border border-dashed border-slate-300 rounded-2xl p-6 text-center mb-6 flex flex-col items-center gap-2">
                <Cpu className="w-8 h-8 text-slate-300" />
                <span className="text-xs text-slate-500 font-medium">Nenhum dispositivo cadastrado.</span>
              </div>
            )}

            <div className="w-full flex flex-col gap-3">
              <button 
                onClick={() => {
                  setTemDispositivos(true);
                  setFeedback({
                    tipo: 'sucesso',
                    titulo: 'Dispositivo Adicionado',
                    mensagem: 'Novo ESP32 pareado com sucesso!'
                  });
                }}
                className="w-full py-3 rounded-2xl bg-[#5F7DE3] hover:bg-[#4d6bd3] text-white font-semibold text-sm transition-all shadow-md shadow-[#5F7DE3]/20 cursor-pointer"
              >
                {temDispositivos ? 'Adicionar Outro Dispositivo' : 'Conectar ESP32'}
              </button>

              <button 
                onClick={() => setShowDevicesModal(false)}
                className="w-full py-3 rounded-2xl bg-slate-500 hover:bg-slate-600 text-white font-semibold text-sm transition-all shadow-xs cursor-pointer"
              >
                Fechar
              </button>
            </div>

          </div>
        </div>
      )}

      {/* MODAL 2: DETALHES DO DISPOSITIVO (SOLICITADO: CARD COMPLETO DO DISPOSITIVO) */}
      {showDeviceDetails && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center z-50 p-4 animate-in fade-in duration-200">
          <div className="bg-white w-full max-w-md rounded-3xl p-6 shadow-2xl border border-slate-100 relative flex flex-col gap-6">
            
            <button 
              onClick={() => setShowDeviceDetails(false)}
              className="absolute top-5 right-5 text-slate-400 hover:text-slate-600 transition-colors p-1 cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-3 border-b border-slate-100 pb-4">
              <div className="w-12 h-12 rounded-2xl bg-[#5F7DE3]/10 text-[#5F7DE3] flex items-center justify-center shrink-0">
                <Cpu className="w-6 h-6" />
              </div>
              <div className="flex flex-col text-left">
                <h3 className="text-lg font-bold text-slate-800">ESP32 Microcontroller</h3>
                <span className="text-xs text-emerald-600 font-semibold flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-500"></span> Conectado e Ativo
                </span>
              </div>
            </div>

            {/* Informações detalhadas do card */}
            <div className="grid grid-cols-2 gap-3 text-left text-xs">
              <div className="bg-slate-50 p-3 rounded-2xl border border-slate-100 flex flex-col gap-1">
                <span className="text-slate-400 text-[10px] uppercase font-bold">Endereço IP</span>
                <span className="font-semibold text-slate-700 flex items-center gap-1">
                  <Wifi className="w-3.5 h-3.5 text-[#5F7DE3]" /> 192.168.1.105
                </span>
              </div>

              <div className="bg-slate-50 p-3 rounded-2xl border border-slate-100 flex flex-col gap-1">
                <span className="text-slate-400 text-[10px] uppercase font-bold">Bateria</span>
                <span className="font-semibold text-slate-700 flex items-center gap-1">
                  <BatteryCharging className="w-3.5 h-3.5 text-emerald-500" /> 100% (Carregando)
                </span>
              </div>

              <div className="bg-slate-50 p-3 rounded-2xl border border-slate-100 flex flex-col gap-1">
                <span className="text-slate-400 text-[10px] uppercase font-bold">Firmware</span>
                <span className="font-semibold text-slate-700">v2.4.1 (Atualizado)</span>
              </div>

              <div className="bg-slate-50 p-3 rounded-2xl border border-slate-100 flex flex-col gap-1">
                <span className="text-slate-400 text-[10px] uppercase font-bold">Endereço MAC</span>
                <span className="font-semibold text-slate-700">24:62:AB:E4:C1:0C</span>
              </div>
            </div>

            <button 
              onClick={() => setShowDeviceDetails(false)}
              className="w-full py-3 rounded-2xl bg-[#5F7DE3] hover:bg-[#4d6bd3] text-white font-semibold text-sm transition-all shadow-md cursor-pointer"
            >
              Entendido
            </button>

          </div>
        </div>
      )}

      {/* MODAL 3: CONFIRMAÇÃO DE EXCLUSÃO (SOLICITADO) */}
      {itemParaExcluir && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center z-50 p-4 animate-in fade-in duration-200">
          <div className="bg-white w-full max-w-sm rounded-3xl p-6 shadow-2xl border border-slate-100 text-center flex flex-col items-center gap-4">
            
            <div className="w-14 h-14 rounded-full bg-rose-100 text-rose-600 flex items-center justify-center shadow-xs">
              <AlertTriangle className="w-7 h-7" />
            </div>

            <div className="flex flex-col gap-1">
              <h3 className="text-lg font-bold text-slate-800">Deseja excluir?</h3>
              <p className="text-xs text-slate-500 leading-relaxed">
                Tem certeza que deseja remover <strong className="text-slate-700">&quot;{itemParaExcluir}&quot;</strong>? Esta ação não poderá ser desfeita.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-3 w-full mt-2">
              <button 
                onClick={() => setItemParaExcluir(null)}
                className="py-3 rounded-2xl bg-slate-100 hover:bg-slate-200 text-slate-600 font-semibold text-xs transition-all cursor-pointer"
              >
                Cancelar
              </button>

              <button 
                onClick={handleConfirmarExclusao}
                className="py-3 rounded-2xl bg-rose-600 hover:bg-rose-700 text-white font-semibold text-xs transition-all shadow-md shadow-rose-600/20 cursor-pointer"
              >
                Sim, Excluir
              </button>
            </div>

          </div>
        </div>
      )}

      {/* MODAL 4: FEEDBACKS DO SISTEMA (SUCESSO, ERRO, ATENÇÃO) */}
      {feedback.tipo && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center z-50 p-4 animate-in fade-in duration-200">
          <div className="bg-white w-full max-w-sm rounded-3xl p-6 shadow-2xl border border-slate-100 text-center flex flex-col items-center gap-4">
            
            {/* Ícone dinâmico por tipo de feedback */}
            {feedback.tipo === 'sucesso' && (
              <div className="w-14 h-14 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center shadow-xs">
                <CheckCircle2 className="w-8 h-8" />
              </div>
            )}

            {feedback.tipo === 'erro' && (
              <div className="w-14 h-14 rounded-full bg-rose-100 text-rose-600 flex items-center justify-center shadow-xs">
                <XCircle className="w-8 h-8" />
              </div>
            )}

            {feedback.tipo === 'atencao' && (
              <div className="w-14 h-14 rounded-full bg-amber-100 text-amber-600 flex items-center justify-center shadow-xs">
                <AlertTriangle className="w-8 h-8" />
              </div>
            )}

            <div className="flex flex-col gap-1">
              <h3 className="text-lg font-bold text-slate-800">{feedback.titulo}</h3>
              <p className="text-xs text-slate-500 leading-relaxed">{feedback.mensagem}</p>
            </div>

            <button 
              onClick={() => setFeedback({ tipo: null, titulo: '', mensagem: '' })}
              className="w-full py-3 rounded-2xl bg-[#5F7DE3] hover:bg-[#4d6bd3] text-white font-semibold text-xs transition-all shadow-md mt-2 cursor-pointer"
            >
              Ok, Entendido
            </button>

          </div>
        </div>
      )}

    </div>
  );
}