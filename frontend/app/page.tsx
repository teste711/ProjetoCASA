'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { 
  User, 
  Mail, 
  MessageSquare, 
  Send, 
  CheckCircle2, 
  FileText, 
  Cpu, 
  HeartHandshake, 
  Sparkles,
  ArrowRight,
  Download
} from 'lucide-react';

export default function Home() {
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [assunto, setAssunto] = useState('');
  const [mensagem, setMensagem] = useState('');
  const [enviado, setEnviado] = useState(false);
  const [activeSection, setActiveSection] = useState('');

  // Identifica qual seção está visível na tela para sublinhar na Navbar
  useEffect(() => {
    const handleScroll = () => {
      const sections = ['sobre', 'projeto', 'equipe', 'contato'];
      const scrollPosition = window.scrollY + 200;

      for (const section of sections) {
        const el = document.getElementById(section);
        if (el) {
          const top = el.offsetTop;
          const height = el.offsetHeight;
          if (scrollPosition >= top && scrollPosition < top + height) {
            setActiveSection(section);
            break;
          }
        }
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!nome || !email || !mensagem) return;
    setEnviado(true);
  };

  // INTEGRANTES EM ORDEM ALFABÉTICA (A -> Z)
  const primeiraLinha = [
    {
      nome: 'Brenno',
      cargo: 'Desenvolvedor Back-end',
      foto: '/brenno.jpeg',
      inicial: 'B',
    },
    {
      nome: 'Eduarda',
      cargo: 'Desenvolvedora Front-end e UI/UX Designer',
      foto: '/eduarda.jpeg',
      inicial: 'E',
    },
    {
      nome: 'Ellen',
      cargo: 'Artista e Desenvolvedora Front-end',
      foto: '/ellen.jpeg',
      inicial: 'E',
    },
  ];

  const segundaLinha = [
    {
      nome: 'Luana',
      cargo: 'Desenvolvedora Front-end',
      foto: '/luana.jpeg',
      inicial: 'L',
    },
    {
      nome: 'Zeus',
      cargo: 'Desenvolvedor Back-end e IoT',
      foto: '/zeus.jpeg',
      inicial: 'Z',
    },
  ];

  const navLinks = [
    { href: '#sobre', label: 'Sobre', id: 'sobre' },
    { href: '#projeto', label: 'Projeto', id: 'projeto' },
    { href: '#equipe', label: 'Equipe', id: 'equipe' },
    { href: '#contato', label: 'Contato', id: 'contato' },
  ];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 flex flex-col font-sans">

      {/* HEADER / NAV BAR */}
      <header className="sticky top-4 z-50 w-full max-w-6xl mx-auto px-6 py-4 flex items-center justify-between bg-white/80 backdrop-blur-md rounded-2xl shadow-sm border border-slate-100">
        
        {/* Logo C.A.S.A */}
        <div className="flex items-center">
          <div className="relative w-16 h-16 flex items-center justify-center shrink-0">
            <Image 
              src="/logo.png" 
              alt="Logo C.A.S.A" 
              width={64} 
              height={64} 
              className="object-contain"
              priority 
            />
          </div>
        </div>

        {/* Menu de Navegação com Sublinhado Ativo */}
        <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-600">
          {navLinks.map((link) => {
            const isActive = activeSection === link.id;
            return (
              <a 
                key={link.id} 
                href={link.href} 
                className={`relative py-1 transition-colors hover:text-[#5F7DE3] ${
                  isActive ? 'text-[#5F7DE3] font-bold' : ''
                }`}
              >
                {link.label}
                {isActive && (
                  <span className="absolute bottom-0 left-0 w-full h-[2.5px] bg-[#5F7DE3] rounded-full transition-all duration-300" />
                )}
              </a>
            );
          })}
        </nav>

        {/* Grupo de Botões */}
        <div className="flex items-center gap-2">
          <Link 
            href="/login"
            className="px-4 py-2 text-sm font-semibold text-white bg-[#5F7DE3] hover:bg-[#4d6bd3] rounded-xl transition-all shadow-sm"
          >
            Entrar 
          </Link>

          <Link 
            href="/cadastro"
            className="px-4 py-2 text-sm font-semibold text-white bg-[#5F7DE3] hover:bg-[#4d6bd3] rounded-xl transition-all shadow-sm"
          >
            Cadastrar 
          </Link>
        </div>

      </header>

      <main className="flex-1 max-w-6xl w-full mx-auto px-6 py-8 flex flex-col gap-16">

        {/* BANNER HERO */}
        <section 
          className="w-full h-80 rounded-3xl flex items-center justify-center shadow-lg relative overflow-hidden mt-2"
          style={{
            background: 'linear-gradient(90deg, #F5AC46 0%, #6586F3 52%, #4D66B8 88%, #3B4E8D 100%)'
          }}
        >
          <div className="text-center text-white p-6 z-10 max-w-2xl">
            <h1 className="text-3xl md:text-5xl font-extrabold mb-3 drop-shadow-sm tracking-tight">
              Projeto C.A.S.A.
            </h1>
            <p className="text-white/90 font-medium text-sm md:text-base leading-relaxed drop-shadow-sm">
              Comunicação Alternativa para Suporte à Autistas: Tecnologia assistiva e IoT promovendo a autonomia e a inclusão comunicacional.
            </p>
          </div>
        </section>

        {/* SEÇÃO SOBRE O PROJETO COM CARDS E TEXTO JUSTIFICADO */}
        <section id="sobre" className="flex flex-col items-center text-center gap-10 py-4 scroll-mt-28">
          <div className="flex flex-col gap-2 max-w-xl mx-auto">
            <h2 className="text-3xl font-bold text-slate-900">Sobre o Projeto</h2>
            <p className="text-xs text-slate-400 font-medium leading-relaxed">
              Unimos hardware interativo e software em nuvem para criar pontes de comunicação no dia a dia.
            </p>
          </div>
          
          {/* Cards de Recursos e Diferenciais */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full">
            
            <div className="bg-white border border-slate-200/80 rounded-3xl p-6 shadow-sm flex flex-col items-center text-center gap-4 hover:border-[#5F7DE3]/50 hover:shadow-md transition-all group">
              <div className="w-14 h-14 rounded-2xl bg-[#5F7DE3]/10 text-[#5F7DE3] flex items-center justify-center group-hover:scale-110 transition-transform">
                <HeartHandshake className="w-7 h-7" />
              </div>
              <div className="flex flex-col gap-1.5">
                <h3 className="font-bold text-slate-800 text-base group-hover:text-[#5F7DE3] transition-colors">
                  Inclusão & Empatia
                </h3>
                <p className="text-xs text-slate-500 leading-relaxed font-normal">
                  Baseado no método PECS (troca de figuras), permitindo que crianças com TEA de níveis 1 e 2 de suporte se expressem com facilidade.
                </p>
              </div>
            </div>

            <div className="bg-white border border-slate-200/80 rounded-3xl p-6 shadow-sm flex flex-col items-center text-center gap-4 hover:border-[#5F7DE3]/50 hover:shadow-md transition-all group">
              <div className="w-14 h-14 rounded-2xl bg-amber-500/10 text-amber-500 flex items-center justify-center group-hover:scale-110 transition-transform">
                <Cpu className="w-7 h-7" />
              </div>
              <div className="flex flex-col gap-1.5">
                <h3 className="font-bold text-slate-800 text-base group-hover:text-[#5F7DE3] transition-colors">
                  Hardware IoT Interativo
                </h3>
                <p className="text-xs text-slate-500 leading-relaxed font-normal">
                  Dispositivo físico microcontrolado (ESP32) equipado com telas IPS, retorno tátil (vibracall) e síntese/gravação de áudios em tempo real.
                </p>
              </div>
            </div>

            <div className="bg-white border border-slate-200/80 rounded-3xl p-6 shadow-sm flex flex-col items-center text-center gap-4 hover:border-[#5F7DE3]/50 hover:shadow-md transition-all group">
              <div className="w-14 h-14 rounded-2xl bg-indigo-500/10 text-indigo-500 flex items-center justify-center group-hover:scale-110 transition-transform">
                <Sparkles className="w-7 h-7" />
              </div>
              <div className="flex flex-col gap-1.5">
                <h3 className="font-bold text-slate-800 text-base group-hover:text-[#5F7DE3] transition-colors">
                  Personalização Total
                </h3>
                <p className="text-xs text-slate-500 leading-relaxed font-normal">
                  Painel de gerenciamento completo onde pais e terapeutas ajustam categorias, cadastram vozes personalizadas e acompanham o desempenho.
                </p>
              </div>
            </div>

          </div>

          {/* Texto descritivo com ALINHAMENTO JUSTIFICADO (text-justify) */}
          <div className="w-full bg-[#FAF8FC] border border-purple-100/80 rounded-3xl p-6 sm:p-10 text-left shadow-xs flex flex-col gap-4">
            <h3 className="text-xl font-extrabold text-slate-800 flex items-center gap-2.5">
              <span className="w-3 h-3 rounded-full bg-[#5F7DE3]"></span>
              O que é o Projeto C.A.S.A.?
            </h3>
            <p className="text-sm sm:text-base text-slate-600 leading-relaxed font-normal text-justify">
              O <strong>C.A.S.A. (Comunicação Alternativa para Suporte à Autistas)</strong> é um ecossistema de tecnologia assistiva desenvolvido para mitigar barreiras na comunicação e interação social de crianças no espectro autista. Integrando um dispositivo físico inteligente com conectividade sem fio a uma plataforma web e móvel, o sistema possibilita que responsáveis e educadores personalizem a prancha de comunicação com pictogramas, categorias de rotina e mensagens de áudio gravadas com a própria voz da família. Ao pressionar um botão, a criança recebe feedback multissensorial simultâneo (imagem, som e vibração), auxiliando na autoexpressão, prevenindo frustrações e promovendo a autonomia cotidiana.
            </p>
          </div>
        </section>

        <hr className="border-slate-200" />

        {/* SEÇÃO DO PROJETO COM IMAGENS */}
        <section id="projeto" className="flex flex-col items-center text-center gap-8 scroll-mt-28">
          <div className="flex flex-col gap-2 max-w-xl mx-auto">
            <h2 className="text-3xl font-bold text-slate-900">Visão Geral do Sistema</h2>
            <p className="text-xs text-slate-400 font-medium leading-relaxed">
              Conheça o dispositivo físico interativo e a plataforma de gerenciamento web do C.A.S.A.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full max-w-5xl">
            
            <div className="bg-white border border-slate-200/80 rounded-3xl p-5 shadow-sm flex flex-col items-center gap-4 hover:border-[#5F7DE3]/50 hover:shadow-md transition-all group overflow-hidden">
              <div className="relative w-full h-64 sm:h-72 rounded-2xl overflow-hidden bg-slate-100">
                <Image 
                  src="/casa.jpeg" 
                  alt="Dispositivo Físico C.A.S.A." 
                  fill 
                  className="object-cover group-hover:scale-105 transition-transform duration-300"
                />
              </div>
              <div className="flex flex-col gap-1 text-center">
                <h3 className="font-bold text-slate-800 text-base group-hover:text-[#5F7DE3] transition-colors">
                  Dispositivo IoT Físico
                </h3>
                <p className="text-xs text-slate-500 leading-relaxed font-normal">
                  Prancha de comunicação com botões físicos, telas IPS coloridas e retorno auditivo e tátil.
                </p>
              </div>
            </div>

            <div className="bg-white border border-slate-200/80 rounded-3xl p-5 shadow-sm flex flex-col items-center gap-4 hover:border-[#5F7DE3]/50 hover:shadow-md transition-all group overflow-hidden">
              <div className="relative w-full h-64 sm:h-72 rounded-2xl overflow-hidden bg-slate-100">
                <Image 
                  src="/sistema.png" 
                  alt="Plataforma de Gerenciamento C.A.S.A." 
                  fill 
                  className="object-cover group-hover:scale-105 transition-transform duration-300"
                />
              </div>
              <div className="flex flex-col gap-1 text-center">
                <h3 className="font-bold text-slate-800 text-base group-hover:text-[#5F7DE3] transition-colors">
                  Plataforma de Gerenciamento
                </h3>
                <p className="text-xs text-slate-500 leading-relaxed font-normal">
                  Dashboard web para personalização de botões, acompanhamento de histórico e estatísticas.
                </p>
              </div>
            </div>

          </div>

          <div className="mt-2">
            <button className="px-8 py-3.5 bg-slate-900 hover:bg-slate-800 text-white text-sm font-semibold rounded-2xl transition-all shadow-md flex items-center gap-2.5 cursor-pointer hover:scale-105 active:scale-95">
              <Download className="w-4 h-4 text-[#5F7DE3]" />
              <span>Baixar App / Documentação do Projeto</span>
            </button>
          </div>
        </section>

        <hr className="border-slate-200" />

        {/* SEÇÃO DA EQUIPE (A -> Z) */}
        <section id="equipe" className="flex flex-col items-center text-center gap-8 scroll-mt-28">
          <h2 className="text-2xl font-bold text-slate-900">Equipe</h2>
          
          <div className="flex flex-col gap-6 w-full max-w-4xl">
            {/* Primeira Linha (Brenno, Eduarda, Ellen) */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full">
              {primeiraLinha.map((membro) => (
                <div 
                  key={membro.nome}
                  className="bg-white border border-slate-200/80 rounded-2xl p-6 shadow-sm flex flex-col items-center text-center gap-3 hover:border-[#5F7DE3]/50 hover:shadow-md transition-all group"
                >
                  <div className="w-20 h-20 rounded-full border-2 border-[#5F7DE3] overflow-hidden shrink-0 relative shadow-xs bg-[#5F7DE3]/10">
                    <Image 
                      src={membro.foto}
                      alt={`Foto de ${membro.nome}`}
                      fill
                      className="object-cover"
                    />
                  </div>

                  <div className="flex flex-col gap-1">
                    <h3 className="font-bold text-slate-800 text-sm group-hover:text-[#5F7DE3] transition-colors">
                      {membro.nome}
                    </h3>
                    <p className="text-[11px] text-slate-500 font-medium leading-snug">
                      {membro.cargo}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {/* Segunda Linha (Luana, Zeus) */}
            <div className="flex flex-col md:flex-row justify-center gap-6 w-full">
              {segundaLinha.map((membro) => (
                <div 
                  key={membro.nome}
                  className="w-full md:w-[calc(33.333%-1rem)] bg-white border border-slate-200/80 rounded-2xl p-6 shadow-sm flex flex-col items-center text-center gap-3 hover:border-[#5F7DE3]/50 hover:shadow-md transition-all group"
                >
                  <div className="w-20 h-20 rounded-full border-2 border-[#5F7DE3] overflow-hidden shrink-0 relative shadow-xs bg-[#5F7DE3]/10">
                    <Image 
                      src={membro.foto}
                      alt={`Foto de ${membro.nome}`}
                      fill
                      className="object-cover"
                    />
                  </div>

                  <div className="flex flex-col gap-1">
                    <h3 className="font-bold text-slate-800 text-sm group-hover:text-[#5F7DE3] transition-colors">
                      {membro.nome}
                    </h3>
                    <p className="text-[11px] text-slate-500 font-medium leading-snug">
                      {membro.cargo}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <hr className="border-slate-200" />

        {/* SEÇÃO DE CONTATO */}
        <section id="contato" className="flex flex-col items-center text-center gap-8 pb-8 scroll-mt-28">
          <div className="flex flex-col gap-2 max-w-md mx-auto">
            <h2 className="text-3xl font-extrabold text-slate-900">Fale Conosco</h2>
            <p className="text-xs text-slate-400 font-medium leading-relaxed">
              Tem alguma dúvida ou quer saber mais sobre o projeto C.A.S.A.? Mande uma mensagem para a nossa equipe!
            </p>
          </div>

          <div className="w-full max-w-xl bg-white border border-slate-200/80 rounded-3xl p-6 sm:p-8 shadow-sm text-left">
            {!enviado ? (
              <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="flex flex-col gap-1.5">
                    <label className="text-xs font-bold text-slate-700">Seu Nome:</label>
                    <div className="relative flex items-center">
                      <User className="w-4 h-4 text-slate-400 absolute left-4 pointer-events-none" />
                      <input 
                        type="text" 
                        placeholder="Ana Silva"
                        value={nome}
                        onChange={(e) => setNome(e.target.value)}
                        className="w-full bg-[#FAF8FC] border border-purple-100/80 rounded-2xl pl-11 pr-4 py-3 text-xs text-slate-700 placeholder:text-slate-400 focus:outline-none focus:border-[#5F7DE3] transition-all"
                        required
                      />
                    </div>
                  </div>

                  <div className="flex flex-col gap-1.5">
                    <label className="text-xs font-bold text-slate-700">Seu E-mail:</label>
                    <div className="relative flex items-center">
                      <Mail className="w-4 h-4 text-slate-400 absolute left-4 pointer-events-none" />
                      <input 
                        type="email" 
                        placeholder="ana@email.com"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="w-full bg-[#FAF8FC] border border-purple-100/80 rounded-2xl pl-11 pr-4 py-3 text-xs text-slate-700 placeholder:text-slate-400 focus:outline-none focus:border-[#5F7DE3] transition-all"
                        required
                      />
                    </div>
                  </div>
                </div>

                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold text-slate-700">Assunto:</label>
                  <div className="relative flex items-center">
                    <FileText className="w-4 h-4 text-slate-400 absolute left-4 pointer-events-none" />
                    <input 
                      type="text" 
                      placeholder="Dúvida, sugestão, parceria..."
                      value={assunto}
                      onChange={(e) => setAssunto(e.target.value)}
                      className="w-full bg-[#FAF8FC] border border-purple-100/80 rounded-2xl pl-11 pr-4 py-3 text-xs text-slate-700 placeholder:text-slate-400 focus:outline-none focus:border-[#5F7DE3] transition-all"
                    />
                  </div>
                </div>

                <div className="flex flex-col gap-1.5">
                  <label className="text-xs font-bold text-slate-700">Sua Mensagem:</label>
                  <div className="relative flex items-start">
                    <MessageSquare className="w-4 h-4 text-slate-400 absolute left-4 top-3.5 pointer-events-none" />
                    <textarea 
                      rows={4}
                      placeholder="Escreva sua mensagem aqui..."
                      value={mensagem}
                      onChange={(e) => setMensagem(e.target.value)}
                      className="w-full bg-[#FAF8FC] border border-purple-100/80 rounded-2xl pl-11 pr-4 py-3 text-xs text-slate-700 placeholder:text-slate-400 focus:outline-none focus:border-[#5F7DE3] transition-all resize-none"
                      required
                    />
                  </div>
                </div>

                <button 
                  type="submit"
                  className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-[#94A7EB] to-[#6A81D6] hover:from-[#8196E6] hover:to-[#5770C9] text-white font-semibold text-sm transition-all shadow-md shadow-[#5F7DE3]/20 flex items-center justify-center gap-2 cursor-pointer mt-2"
                >
                  <Send className="w-4 h-4" />
                  <span>Enviar Mensagem</span>
                </button>

              </form>
            ) : (
              <div className="flex flex-col items-center text-center gap-4 py-6 animate-in fade-in duration-300">
                <div className="w-14 h-14 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center shadow-xs">
                  <CheckCircle2 className="w-8 h-8" />
                </div>
                <h3 className="text-base font-bold text-slate-800">Mensagem Enviada!</h3>
                <p className="text-xs text-slate-500 leading-relaxed max-w-sm">
                  Obrigado pelo contato, <span className="font-semibold text-slate-700">{nome}</span>! Nossa equipe responderá no e-mail fornecido em breve.
                </p>
                <button 
                  onClick={() => {
                    setEnviado(false);
                    setNome('');
                    setEmail('');
                    setAssunto('');
                    setMensagem('');
                  }}
                  className="text-xs text-[#5F7DE3] font-semibold hover:underline mt-2 cursor-pointer"
                >
                  Enviar outra mensagem
                </button>
              </div>
            )}
          </div>
        </section>

      </main>

      {/* FOOTER COMPLETO E ESTILIZADO */}
      <footer className="w-full bg-white border-t border-slate-200 mt-12 py-12 text-slate-600">
        <div className="max-w-6xl mx-auto px-6 grid grid-cols-1 md:grid-cols-4 gap-8">
          
          <div className="flex flex-col gap-4 md:col-span-1">
            <div className="flex items-center gap-3">
              <div className="relative w-10 h-10 flex items-center justify-center">
                <Image 
                  src="/logo.png" 
                  alt="Logo C.A.S.A" 
                  width={40} 
                  height={40} 
                  className="object-contain"
                />
              </div>
              <span className="font-extrabold text-[#5F7DE3] text-lg tracking-tight">C.A.S.A.</span>
            </div>
            <p className="text-xs text-slate-500 leading-relaxed">
              Comunicação Alternativa para Suporte à Autistas. Tecnologia assistiva focada em promover autonomia, comunicação fluida e inclusão social.
            </p>
          </div>

          <div className="flex flex-col gap-3">
            <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">Navegação</h4>
            <ul className="flex flex-col gap-2 text-xs text-slate-500">
              <li><a href="#sobre" className="hover:text-[#5F7DE3] transition-colors">Sobre o Projeto</a></li>
              <li><a href="#projeto" className="hover:text-[#5F7DE3] transition-colors">Recursos & Download</a></li>
              <li><a href="#equipe" className="hover:text-[#5F7DE3] transition-colors">Nossa Equipe</a></li>
              <li><a href="#contato" className="hover:text-[#5F7DE3] transition-colors">Fale Conosco</a></li>
            </ul>
          </div>

          <div className="flex flex-col gap-3">
            <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">Acesso ao Sistema</h4>
            <ul className="flex flex-col gap-2 text-xs text-slate-500">
              <li>
                <Link href="/login" className="hover:text-[#5F7DE3] transition-colors flex items-center gap-1">
                  <span>Área do Responsável</span>
                  <ArrowRight className="w-3 h-3 text-[#5F7DE3]" />
                </Link>
              </li>
              <li>
                <Link href="/cadastro" className="hover:text-[#5F7DE3] transition-colors flex items-center gap-1">
                  <span>Criar Nova Conta</span>
                  <ArrowRight className="w-3 h-3 text-[#5F7DE3]" />
                </Link>
              </li>
            </ul>
          </div>

          <div className="flex flex-col gap-3">
            <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">Institucional</h4>
            <p className="text-xs text-slate-500 leading-relaxed">
              Projeto acadêmico desenvolvido na <strong>Fatec Praia Grande</strong> no curso de Desenvolvimento de Software Multiplataforma.
            </p>
          </div>

        </div>

        <div className="max-w-6xl mx-auto px-6 mt-10 pt-6 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between text-[11px] text-slate-400 gap-2">
          <p>© 2026 Projeto C.A.S.A. Todos os direitos reservados.</p>
          <p>Desenvolvido pela Equipe Selenes.</p>
        </div>
      </footer>

    </div>
  );
}