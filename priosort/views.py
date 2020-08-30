from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
import random, json


def home(response):
    return render(response, 'home.html')

def nuevo(response):
    return render(response, 'nuevo.html')

def handle_uuid(response, more):
    try:
        s = Sorteo.objects.get(pk=more)
        return sorteo(response, more)
    except Sorteo.DoesNotExist:
        try:
            s = Sorteo.objects.get(id_asignacion=more)
            return asignar(response, more)
        except Sorteo.DoesNotExist:
            return redirect('/')


def sorteo(response, sorteo_id):
    try:
        sorteo = Sorteo.objects.get(pk=sorteo_id)
    except Sorteo.DoesNotExist:
        raise Http404("Sorteo does not exist")

    sorteo_info = dict()
    sorteo_info['nombre'] = sorteo.nombre
    sorteo_info['id'] = sorteo.id
    sorteo_info['asignacion'] = sorteo.id_asignacion
    sorteo_info['personas'] = []
    sorteo_info['hecho'] = True

    personas = Persona.objects.filter(sorteo=sorteo)

    if len(Resultado.objects.filter(sorteo=sorteo)) > 0:
        for persona in personas:
            sorteo_info['personas'].append({
                'nombre':   persona.nombre,
                'item':     Resultado.objects.filter(persona=persona)[0].item.nombre
            })
        
        orden = dict()
        
        for r in Resultado.objects.filter(sorteo=sorteo):
            orden[r.orden] = r.persona.nombre

        print(orden)
        sorteo_info['orden'] = []
        
        for i in range(len(Resultado.objects.filter(sorteo=sorteo))):
            sorteo_info['orden'].append(orden[i])

        return render(response, 'sorteo-hecho.html', sorteo_info)
    else:
        for persona in personas:
            sorteo_info['personas'].append({
                'nombre':   persona.nombre,
                'hecho':    len(Prioridad.objects.filter(persona=persona)) > 0,
                'id':       persona.id
            })
            if len(Prioridad.objects.filter(persona=persona)) == 0:
                sorteo_info['hecho'] = False

        return render(response, 'sorteo.html', sorteo_info)

def eliminar_asignacion(response, persona_id):
    try:
        persona = Persona.objects.get(pk=persona_id)
    except Persona.DoesNotExists:
        return redirect('/')
    
    Prioridad.objects.filter(persona=persona).delete()
    print(Prioridad.objects.filter(persona=persona))

    return redirect(f'/{persona.sorteo.id}')

def sortear(response, sorteo_id):
    try:
        sorteo = Sorteo.objects.get(pk=sorteo_id)
    except Sorteo.DoesNotExist:
        raise Http404("Sorteo does not exist")

    personas = [p.id for p in Persona.objects.filter(sorteo=sorteo)]

    proceed = True
    for persona in personas:
        if len(Prioridad.objects.filter(persona=persona)) == 0:
            proceed = False

    if not proceed:
        return redirect(f'/{sorteo_id}')
    
    prioridades = dict()
    for persona in personas:
        prioridades[persona] = []
        for p in Prioridad.objects.filter(persona=persona).order_by('-prioridad'):
            prioridades[persona].append(p.item.id)
    
    random.shuffle(personas)

    print(prioridades)

    asignacion = dict()

    for persona in personas:
        asignacion[persona] = prioridades[persona][0]
        for per in personas:
            if asignacion[persona] in prioridades[per]:
                prioridades[per].remove(asignacion[persona])

    i = 0
    for persona in personas:
        r = Resultado(persona=Persona.objects.get(pk=persona), \
            item=Item.objects.get(pk=asignacion[persona]), \
            sorteo=Sorteo.objects.get(pk=sorteo_id), \
            orden=i
        )
        r.save()
        i += 1
    
    return redirect(f'/{sorteo_id}')

def asignar(response, id_asignacion):
    try:
        sorteo = Sorteo.objects.get(id_asignacion=id_asignacion)
    except Sorteo.DoesNotExist:
        return redirect('/')

    sorteo_info = dict()
    sorteo_info['nombre'] = sorteo.nombre
    sorteo_info['id'] = sorteo.id
    sorteo_info['asignacion'] = sorteo.id_asignacion
    sorteo_info['personas_nohecho'] = []
    sorteo_info['hecho'] = True

    personas = Persona.objects.filter(sorteo=sorteo)

    for persona in personas:
        if len(Prioridad.objects.filter(persona=persona)) == 0:
            sorteo_info['personas_nohecho'].append({
                'nombre':   persona.nombre,
                'id':       persona.id
            })

    sorteo_info['items'] = []

    items = Item.objects.filter(sorteo=sorteo)
    
    for item in items:
        sorteo_info['items'].append({
            'nombre':   item.nombre,
            'id':       item.id
        })

    if len(sorteo_info['personas_nohecho']) == 0:
        sorteo_info['message'] = "Todas las personas han guardado sus resultados. Ponte en contacto con quien haya hecho el sorteo si crees que esto es un error."

    return render(response, 'asignar.html', sorteo_info)

def populate(request):
    s = Sorteo(nombre="Habitación Piso")
    s.save()

    items = ["Habitación 1", "Habitación 2", "Habitación 3", "Habitación 4"]
    personas = ["Javi", "Julio", "Alberto", "Ángel"]

    _items = []

    for it in items:
        i = Item(nombre=it, sorteo=s)
        _items.append(i)
        i.save()
    
    for persona in personas:
        p = Persona(nombre=persona, sorteo=s)
        p.save()

        random.shuffle(_items)
        prio = 1
        if persona != "Julio":
            for it in _items:
                pr = Prioridad(prioridad=prio, persona=p, item=it)
                pr.save()
                prio += 1
        
    return redirect(f'/{s.id}')

def aniadir_asignacion(request):
    if request.method == 'POST':
        post = request.POST.get('data')
        response_data = {}
        post = json.loads(post)

        persona = Persona.objects.get(pk=post['persona'])
        prioridades = [int(p) for p in post['prioridades']]

        if len(Prioridad.objects.filter(persona=persona)) > 0:
            response_data['result'] = 'ERR1'
        else:
            prio = 1
            for prioridad in prioridades:
                it = Item.objects.get(pk=prioridad)
                pr = Prioridad(prioridad=prio, persona=persona, item=it)
                pr.save()

            response_data['result'] = 'OK'
    else:
        response_data = {}
        response_data['result'] = 'NOTOK'
    
    return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )

def nuevo_sorteo(request):
    if request.method == 'POST':
        post = request.POST.get('data')
        response_data = {}
        post = json.loads(post)

        try:
            s = Sorteo(nombre=post['nombre'])
            s.save()

            for item in post['items']:
                i = Item(nombre=item, sorteo=s)
                i.save()
            
            for persona in post['personas']:
                p = Persona(nombre=persona, sorteo=s)
                p.save()

            response_data['result'] = 'OK'
            response_data['sorteo_id'] = str(s.id)
        
        except Exception:
            response_data['result'] = 'NOTOK'            
    else:
        response_data = {}
        response_data['result'] = 'NOTOK'
    
    return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )