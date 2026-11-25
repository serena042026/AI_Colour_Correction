"""Small, explainable colour-correction prototype; not a calibrated colourimeter."""
import base64, io, json, os, datetime
from PIL import Image, ImageEnhance, ImageStat
import re

HERE = os.path.dirname(__file__)
LOG = os.path.join(HERE, 'colour_tool_log.jsonl')
MAX_BYTES = 8_000_000

def _decode(value):
    if not isinstance(value, str) or ',' not in value or not value.startswith('data:image/'):
        raise ValueError('Upload a JPEG or PNG image.')
    raw = base64.b64decode(value.split(',',1)[1], validate=True)
    if len(raw) > MAX_BYTES: raise ValueError('Image is too large (8 MB limit).')
    im = Image.open(io.BytesIO(raw))
    if im.format not in ('PNG', 'JPEG', 'WEBP'): raise ValueError('Use PNG, JPEG or WEBP.')
    im.load()
    if im.width * im.height > 16_000_000: raise ValueError('Image dimensions are too large.')
    im = im.convert('RGB'); im.thumbnail((1100,1100))
    return im

def _encode(im):
    out=io.BytesIO(); im.save(out, format='JPEG',quality=85)
    return 'data:image/jpeg;base64,'+base64.b64encode(out.getvalue()).decode()

def analyse(payload):
    im=_decode(payload.get('image'))
    mode=payload.get('reference','none')
    if mode not in ('none','paper','chart'): raise ValueError('Invalid reference mode.')
    warnings=[]; status='low'; gains=(1.,1.,1.); patch=None
    source=payload.get('reference_source','same' if mode!='none' else 'none')
    if source not in ('none','same','separate'): raise ValueError('Invalid reference source.')
    if mode!='none' and source=='none': raise ValueError('Choose a reference source.')
    ref_im=im
    if mode!='none' and source=='separate':
        if not payload.get('reference_image'):
            raise ValueError('Upload a separate reference photo first.')
        ref_im=_decode(payload['reference_image'])
        warnings.append('Separate reference photo: lighting and camera settings cannot be verified. Colour reliability remains LOW even if the patch passes visual checks.')
    if mode=='none':
        warnings.append('No reference: colour correction is an approximate visual adjustment, not a measurement of true garment colour.')
    else:
        box=payload.get('box')
        if not isinstance(box,list) or len(box)!=4 or not all(isinstance(x,(int,float)) for x in box):
            warnings.append('Select a reference rectangle on the '+('reference photo' if source=='separate' else 'clothing photo')+' before analysis. No reference-based correction applied.')
        else:
            x1,y1,x2,y2=[max(0,min(1,float(x))) for x in box]
            x1,x2=sorted((x1,x2)); y1,y2=sorted((y1,y2))
            if (x2-x1)<.025 or (y2-y1)<.025:
                warnings.append('Reference area too small; select a larger region.')
            else:
                patch=ref_im.crop((int(x1*ref_im.width),int(y1*ref_im.height),max(int(x1*ref_im.width)+1,int(x2*ref_im.width)),max(int(y1*ref_im.height)+1,int(y2*ref_im.height))))
                small=patch.copy(); small.thumbnail((160,160))
                pixels=list(small.getdata()); means=ImageStat.Stat(small).mean
                clipped=sum(1 for p in pixels if max(p)>=250)/len(pixels)
                dark=sum(1 for p in pixels if sum(p)/3<110)/len(pixels)
                spread=sum(ImageStat.Stat(small).stddev)/3
                if clipped>.08: warnings.append('Reference rejected: approximately %.0f%% of sampled pixels are near clipping/overexposure.'%(clipped*100))
                if dark>.12: warnings.append('Reference rejected: substantial dark/shadowed areas detected.')
                if spread>38: warnings.append('Reference rejected: reference area is not sufficiently uniform (possible shadows, patterns or edges).')
                if mode=='chart':
                    warnings.append('A calibrated colour chart requires known patch values. This prototype cannot calibrate an arbitrary chart; no chart-based correction applied.')
                elif not any('rejected' in w for w in warnings):
                    if min(means)<95: warnings.append('Reference rejected: selected paper region is too dark.')
                    else:
                        target=sum(means)/3
                        gains=tuple(max(.72,min(1.28,target/max(1,m))) for m in means)
                        status='low' if source=='separate' else 'medium'
                        warnings.append('Approximate white-paper neutralisation applied to the CLOTHING photo using the selected reference region. White paper is not a calibrated colour standard.')
    brightness=float(payload.get('brightness',1)); saturation=float(payload.get('saturation',1))
    warmth=float(payload.get('warmth',0)); contrast=float(payload.get('contrast',1))
    if not (-0.5 <= warmth <= 0.5 and 0.5 <= contrast <= 1.5):
        raise ValueError('Warmth must be -0.5 to 0.5; contrast must be 0.5 to 1.5.')
    if not (.5<=brightness<=1.5 and .5<=saturation<=1.5): raise ValueError('Brightness and saturation must be between 0.5 and 1.5.')
    # A deliberate global preview; garment segmentation is not claimed.
    if gains!=(1.,1.,1.):
        im=im.point([max(0,min(255,int(i*g))) for g in gains for i in range(256)])
    if abs(warmth)>0.0001:
        # A bounded warm/cool RGB preview, not calibrated white balance.
        red, green, blue=im.split()
        rg=max(0.6,min(1.4,1+warmth*.45)); bg=max(0.6,min(1.4,1-warmth*.45))
        red=red.point(lambda x: min(255,round(x*rg)))
        blue=blue.point(lambda x: min(255,round(x*bg)))
        im=Image.merge('RGB',(red,green,blue))
    im=ImageEnhance.Brightness(im).enhance(brightness)
    im=ImageEnhance.Color(im).enhance(saturation)
    im=ImageEnhance.Contrast(im).enhance(contrast)
    warnings.append('Preview affects the whole image; garment-only segmentation and true-colour accuracy are not implemented.')
    return {'preview':_encode(im),'confidence_label':status,'warnings':warnings,'reference_used':gains!=(1.,1.,1.),
            'settings':{'reference':mode,'reference_source':source,'brightness':brightness,'saturation':saturation,'warmth':warmth,'contrast':contrast,'box':payload.get('box')},
            'reply':'Preview generated. Review the original and adjusted image before accepting.'}

def confirm(payload):
    settings = payload.get("settings")

    # 1. Validate the proposed adjustment
    if not isinstance(settings, dict):
        raise ValueError("No proposed adjustment to confirm")

    for name, (minimum, maximum) in LIMITS.items():
        if name not in settings:
            raise ValueError(f"Missing colour parameter: {name}")

        value = settings[name]

        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"Invalid value for {name}: must be a number")

        if not (minimum <= value <= maximum):
            raise ValueError(
                f"Invalid {name}: {value}. "
                f"Allowed range is {minimum} to {maximum}"
            )

    # 2. Record the user's confirmed preview
    record = {
        "time": datetime.datetime.now().isoformat(timespec="seconds"),
        "tool": "accept_colour_preview",
        "arguments": settings,
        "confirmed_by": "user",
        "result": {"status": "accepted_preview_only"}
    }

    # 3. Write the operation to the local log
    with open(LOG, "a", encoding="utf8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return {
        "reply": (
            "Preview accepted and logged locally. "
            "This does not establish true colour accuracy."
        )
    }

# Intent-based, bounded feedback. This does NOT use an LLM or claim to understand every sentence.
FEEDBACK_RULES = [
    ('too grey / dull', [r'grey', r'gray', r'dull', r'washed.out', r'灰', r'暗淡', r'不鲜艳'], {'saturation': .15}),
    ('too yellow / warm', [r'yellow', r'too warm', r'黄', r'偏暖'], {'warmth': -.12}),
    ('too blue / cool', [r'blue', r'too cool', r'蓝', r'偏冷'], {'warmth': .12}),
    ('too dark', [r'dark', r'暗', r'太黑'], {'brightness': .12}),
    ('too bright', [r'bright', r'太亮', r'过亮'], {'brightness': -.12}),
    ('too saturated', [r'oversaturat', r'too vivid', r'too saturated', r'过于鲜艳', r'太艳', r'饱和度太高'], {'saturation': -.15}),
    ('low contrast', [r'flat', r'low contrast', r'对比度低', r'没层次'], {'contrast': .12}),
    ('too much contrast', [r'too much contrast', r'high contrast', r'对比度太高'], {'contrast': -.12}),
]
LIMITS={'brightness':(.5,1.5),'saturation':(.5,1.5),'warmth':(-.5,.5),'contrast':(.5,1.5)}

def interpret_feedback(payload):
    message=str(payload.get('message','')).strip()
    if not message or len(message)>500: raise ValueError('Enter feedback of 1–500 characters.')
    values={k:float(payload.get('settings',{}).get(k, 0 if k=='warmth' else 1)) for k in LIMITS}
    if any(not (lo<=values[k]<=hi) for k,(lo,hi) in LIMITS.items()): raise ValueError('Invalid adjustment values.')
    msg=message.lower()
    # Check specific phrase before generic keywords (e.g. "too bright" vs "too grey").
    order=[5,4,3,1,2,7,6,0]
    matches=[FEEDBACK_RULES[i] for i in order if any(re.search(pattern,msg) for pattern in FEEDBACK_RULES[i][1])]
    if not matches:
        return {'understood':False,'reply':'I could not confidently interpret that feedback. Try: too grey, too yellow, too blue, too dark, too bright, too saturated, or low contrast. No change has been made.','settings':values}
    # One bounded adjustment per turn: ambiguous compound messages are not silently merged.
    label,_,changes=matches[0]
    new=values.copy()
    for key,delta in changes.items():
        lo,hi=LIMITS[key];new[key]=round(min(hi,max(lo,new[key]+delta)),2)
    if new==values:
        return {'understood':True,'reply':'Adjustment limit reached. No further change was applied.','settings':values,'intent':label}
    return {'understood':True,'intent':label,'settings':new,'reply':f'I interpreted your feedback as “{label}”. I propose a small {list(changes)[0]} adjustment. Review the new preview before accepting it. This does not verify the garment’s real colour.'}
