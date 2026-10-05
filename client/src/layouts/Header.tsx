import { useEffect, useRef, useState } from 'react';
import { FaEarListen } from "react-icons/fa6";
import { IoIosNotificationsOutline } from "react-icons/io";
import { IoSearch } from "react-icons/io5";
import { RiSpeakLine } from "react-icons/ri";
import { RxDropdownMenu } from "react-icons/rx";
import { useLocation, useNavigate } from 'react-router-dom';
import api from '../utils/api';
import { sidebarItems } from '../utils/sidebar';
import { Field } from '../types/header';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { waitForQueueJob } from '../utils/queue-jobs';

export const Header = () => {
  const [state, setState] = useState({
    menu: false,
    listen: false,
    voice: false,
    pop: false,
    popup: false,
    activeIndex: 0,
    fields: [] as Field[],
    loading: false,
    audioBlob: null as Blob | null,
    type: "",
    isRecording: false,
    store: { name: "", email: "" },
    searchQuery: '',
    searchResults: [] as any[]
  });

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const nav = useNavigate();
  const location = useLocation();

  const handleInputChange = (idx: number, value: string) => {
    const updatedFields = [...state.fields];
    updatedFields[idx] = { ...updatedFields[idx], value };
    setState(prevState => ({ ...prevState, fields: updatedFields }));
  };

  const handleUploadPopUpClose = async (type: string) => {
    const data = state.fields.reduce((acc, field) => {
      acc[field.name] = field.value;
      return acc;
    }, {} as Record<string, string>);

    try {
      let response;
      switch (type) {
        case "INSERT":
          response = await api.post(`/query/upload/create/`, data);
          toast.success('Data inserted successfully.');
          break;

        case "UPDATE":
          response = await api.put(`/query/upload/update/`, data);
          toast.success('Data updated successfully.');
          break;

        case "DELETE":
          response = await api.delete(`/query/upload/delete/`);
          toast.success('Data deleted successfully.');
          break;

        default:
          toast.error('Invalid action type.');
          return;
      }

      console.log(response);

      setState(prevState => ({ ...prevState, popup: false, fields: [], type: "" }));

    } catch (error) {
      toast.error('Error processing the request. Please try again.');
    }
  };

  useEffect(() => {
    const fetchStoreName = async () => {
      try {
        const response = await api.get(`/settings/store/get/`);
        setState(prevState => ({ ...prevState, store: response.data }));
      } catch (error) {
        toast.error('Error fetching store name.');
      }
    };
    fetchStoreName();
  }, []);

  const performSearch = async () => {
    if (state.searchQuery.trim()) {
      const toastId = toast.loading('Building query...');
      try {
        setState(prevState => ({ ...prevState, loading: true }));
        const queued = await api.post(`/query/generate/`, { prompt: state.searchQuery });
        const completed = await waitForQueueJob(queued.data.job_id);
        toast.update(toastId, {
          render: 'Query ready',
          type: 'success',
          isLoading: false,
          autoClose: 1800,
        });
        nav('/query', {
          state: { queryResponse: completed.result, header: 'Generated Query' },
        });
      } catch (error) {
        toast.update(toastId, {
          render: 'Unable to generate a query. Please try again.',
          type: 'error',
          isLoading: false,
          autoClose: 3200,
        });
      } finally {
        setState(prevState => ({ ...prevState, loading: false }));
      }
    } else {
      setState(prevState => ({ ...prevState, searchResults: [] }));
    }
  };

  const startRecording = async () => {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        if (mediaRecorderRef.current) {
          mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
        }
        const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
        mediaRecorderRef.current = mediaRecorder;
        audioChunksRef.current = [];
        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunksRef.current.push(event.data);
          }
        };
        mediaRecorder.onstop = () => {
          if (audioChunksRef.current.length > 0) {
            const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
            setState(prevState => ({ ...prevState, audioBlob }));
          } else {
            toast.error("I couldn't hear anything. Try recording again.");
          }
        };
        mediaRecorder.start();
        setState(prevState => ({ ...prevState, isRecording: true }));
      } catch (error) {
        toast.error('Microphone access was blocked.');
      }
    } else {
      toast.error('Voice search is not supported in this browser.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && state.isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      setState(prevState => ({ ...prevState, isRecording: false }));
    }
  };

  useEffect(() => {
    if (state.listen) {
      startRecording();
    } else {
      stopRecording();
    }
  }, [state.listen]);

  useEffect(() => {
    if (state.audioBlob) {
      handleUpload();
    }
  }, [state.audioBlob]);

  const handleUpload = async () => {
    if (state.audioBlob) {
      const formData = new FormData();
      formData.append('file', new File([state.audioBlob], 'audio.webm', { type: 'audio/webm' }));
      const toastId = toast.loading('Understanding audio...');
      setState(prevState => ({ ...prevState, loading: true }));
      try {
        const queued = await api.post(`/query/upload/`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        const completed = await waitForQueueJob(queued.data.job_id);
        toast.update(toastId, {
          render: 'Voice query ready',
          type: 'success',
          isLoading: false,
          autoClose: 1800,
        });
        nav('/query', {
          state: { queryResponse: completed.result, header: 'Voice Query Results' },
        });

      } catch (error: any) {
        toast.update(toastId, {
          render: 'Unable to process the audio. Please try again.',
          type: 'error',
          isLoading: false,
          autoClose: 3200,
        });
        console.log('Error occurred:', error);
      } finally {
        setState(prevState => ({ ...prevState, loading: false }));
      }
    } else {
      toast.error('No audio data available for upload.');
    }
  };

  return (
    <header className='Header_Container'>
      <h1><span className="Header_Brand_Mark"><FaEarListen /></span>EchoCart</h1>
      <div className="Search_Container">
        {state.listen ? (
          <>
            <p>Listening...</p>
            <FaEarListen />
          </>
        ) : (
          <>
            <IoSearch className="Header_Search_Icon" />
            <input
              type="text"
              placeholder="Ask your store anything..."
              value={state.searchQuery}
              onChange={(e) => setState(prevState => ({ ...prevState, searchQuery: e.target.value }))}
              onKeyDown={(e) => e.key === 'Enter' && performSearch()}
            />
            <button
              className="Header_Voice_Button"
              type="button"
              aria-label="Search by voice"
              onClick={() => setState(prevState => ({ ...prevState, voice: !state.voice }))}
            >
              <RiSpeakLine />
            </button>
          </>
        )}
      </div>

      {state.pop && (
        <ul className='Pop_Search_Container'>
          <li>Product</li>
          <li>Product</li>
          {state.loading && <span className="Header_Loading_Pulse" role="status" aria-label="Working" />}
        </ul>
      )}

      {state.loading && <span className="Header_Loading_Pulse" role="status" aria-label="Working" />}

      <div className="RightHand_Container">
        <p className="Exclusive_Store">{state.store.name || "My store"}</p>
        <button className="Header_Icon_Button" type="button" aria-label="Notifications"><IoIosNotificationsOutline /></button>
        <div className="Image_Container" aria-label="Account profile">
          <span>{(state.store.name || state.store.email || 'A').trim().charAt(0).toUpperCase()}</span>
        </div>
      </div>

      <button
        type="button"
        aria-label={state.menu ? "Close navigation menu" : "Open navigation menu"}
        aria-expanded={state.menu}
        onClick={() => setState(prevState => ({ ...prevState, menu: !state.menu }))}
        className="Mobile_Menu"
      >
        <RxDropdownMenu />
      </button>

      {state.menu && (
        <nav className="Mobile_Menu_Nav">
          {sidebarItems.map((obj, index) => (
            <button
              key={obj.itemName}
              type="button"
              onClick={() => {
                setState(prevState => ({ ...prevState, activeIndex: index, menu: false }));
                nav(`/${obj.itemName}`);
              }}
              className={location.pathname.split('/').includes(obj.itemName) || (location.pathname === '/' && index === 0) ? 'Active_List' : ''}>
              <span className="List_icon" aria-hidden="true">{obj.icon}</span>
              <span>{obj.itemName.charAt(0).toUpperCase() + obj.itemName.slice(1)}</span>
            </button>
          ))}
        </nav>
      )}

      {state.voice && (
        <button
          onClick={() => setState(prevState => ({ ...prevState, voice: false, listen: true }))}
          className="Search_By_Voice">
          Search By Voice
        </button>
      )}
      {state.listen && (
        <button
          onClick={() => setState(prevState => ({ ...prevState, listen: false }))}
          className="Search_By_Voice Stop_Voice">
          Stop recording
        </button>
      )}


      {state.popup && (
        <div className="Header_Popup popup-overlay">
          <div className="popup-content">

            <div className="form-group">
              <h2>Carry Out Action</h2>

              {state.fields.map((field, idx) => (
                <div key={idx}>
                  <label>{field.name}</label>
                  <input
                    type="text"
                    value={field.value}
                    onChange={(e) => handleInputChange(idx, e.target.value)}
                  />
                </div>
              ))}

              <button className='Popup_submit' onClick={() => handleUploadPopUpClose(state.type)}>Submit</button>
              <button onClick={() => setState(prevState => ({ ...prevState, fields: [], popup: false, type: "" }))}>Close</button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
};
