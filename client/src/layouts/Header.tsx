import { useEffect, useRef, useState } from 'react';
import { FaEarListen } from "react-icons/fa6";
import { IoIosNotificationsOutline } from "react-icons/io";
import { IoSearch } from "react-icons/io5";
import { RiSpeakLine } from "react-icons/ri";
import { RxDropdownMenu } from "react-icons/rx";
import { useNavigate } from 'react-router-dom';
import ProfileImg from "../assets/profileimg.jfif";
import api from '../utils/api';
import { sideBarArrayList } from '../utils/sidebar';
import { Field } from '../types/header';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { ClipLoader } from 'react-spinners';

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
      try {
        const response = await api.get(`query/search/`, { params: { query: state.searchQuery } });
        setState(prevState => ({ ...prevState, searchResults: response.data }));
      } catch (error) {
        toast.error('Error performing search.');
      }
    } else {
      setState(prevState => ({ ...prevState, searchResults: [] }));
    }
  };

  useEffect(() => {
    performSearch();
  }, [state.searchQuery]);

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
            toast.error("No audio chunks available.");
          }
        };
        mediaRecorder.start();
        setState(prevState => ({ ...prevState, isRecording: true }));
      } catch (error) {
        toast.error('Error accessing microphone.');
      }
    } else {
      toast.error('getUserMedia not supported on this browser.');
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
      setState(prevState => ({ ...prevState, loading: true }));
      try {
        const response = await api.post(`/query/upload/`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        console.log(response)
        const parsed_response = JSON.parse(response.data.results);

        switch (response.data.type) {
          case "SELECT":
            console.log(parsed_response)
            nav('/query', { state: { data: parsed_response, header: 'Query Results' } });
            break;
          case "UPDATE":
            if (parsed_response.fields) {

              const fieldsArray: Field[] = Object.entries(parsed_response.fields).map(([name, value]) => ({ name, value: String(value) }));
              setState(prevState => ({ ...prevState, popup: true, fields: fieldsArray, type: response.data.type }));
            }
            break;
          case "INSERT":
            if (parsed_response.fields) {

              const fieldsArray: Field[] = Object.entries(parsed_response.fields).map(([name, value]) => ({ name, value: String(value) }));
              setState(prevState => ({ ...prevState, popup: true, fields: fieldsArray, type: response.data.type }));
            } else {
              toast.success(parsed_response.message);
            }
            break;

          case "DELETE":
            if (parsed_response.fields) {

              const fieldsArray: Field[] = Object.entries(parsed_response.fields).map(([name, value]) => ({ name, value: String(value) }));
              setState(prevState => ({ ...prevState, popup: true, fields: fieldsArray, type: response.data.type }));
            } else {
              toast.success(parsed_response.message);
            }
            break;
          default:
            toast.error("Unknown action type. Please try again.");
            break;
        }

      } catch (error: any) {
        if (error.response && error.response.status === 500) {
          toast.error('Unable to process your audio request. Please try again.');
          console.log('Error occurred:', error);
        } else {
          toast.error('Unable to find what you\'re looking for. Please try again.');
          console.log('Error occurred:', error);
        }
      } finally {
        setState(prevState => ({ ...prevState, loading: false }));
      }
    } else {
      toast.error('No audio data available for upload.');
    }
  };

  return (
    <div className='Header_Container'>
      <h1>EchoCart</h1>
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
              placeholder="Search anything..."
              value={state.searchQuery}
              onChange={(e) => setState(prevState => ({ ...prevState, searchQuery: e.target.value }))}
              onKeyDown={(e) => e.key === 'Enter' && performSearch()}
            />
            <RiSpeakLine onClick={() => setState(prevState => ({ ...prevState, voice: !state.voice }))} />
          </>
        )}
      </div>

      {state.pop && (
        <ul className='Pop_Search_Container'>
          <li>Product</li>
          <li>Product</li>
          {state.loading && <div className="loading-spinner"></div>}
        </ul>
      )}

      {state.loading && <ClipLoader color="#000000" size={35} />}

      <div className="RightHand_Container">
        <p className="Exclusive_Store">{state.store.name || "Store Name"}</p>
        <IoIosNotificationsOutline />
        <div className="Image_Container">
          <img src={ProfileImg} alt="profile" />
        </div>
      </div>

      <div onClick={() => setState(prevState => ({ ...prevState, menu: !state.menu }))} className="Mobile_Menu">
        <RxDropdownMenu />
      </div>

      {state.menu && (
        <nav className="Mobile_Menu_Nav">
          {sideBarArrayList.map((obj, index) => (
            <button
              key={index}
              onClick={() => {
                setState(prevState => ({ ...prevState, activeIndex: index, menu: false }));
                nav(`/${obj.itemName}`);
              }}
              className={state.activeIndex === index ? 'Active_List' : ''}>
              <p className="List_icon">{obj.icon}</p>
              <p>{obj.itemName}</p>
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
    </div>
  );
};
