MOVE_EFFECTS = {
    'HP': 'hp',
    'MP': 'mp',
    'AD': 'attack_dmg',
    'SAD': 'spc_attack_dmg',
}


def is_dmg_move_type(movetype):
    return movetype == 'HP'


def apply_effect_stat(current_magnitude, buff):
    buff *= 0.01
    current_magnitude *= (1.0 + buff)
    return current_magnitude


def apply_item(entity, item):
    target_var = MOVE_EFFECTS.get(item.type)
    magnitude = item.effect_magnitude
    current_value = getattr(entity,
                            target_var)
    setattr(entity,
            target_var,
            current_value + magnitude
            )
    entity.save()


def apply_move(agent, entity, move):
    target_var = MOVE_EFFECTS.get(move.type)
    magnitude = move.effect_magnitude
    if move.type == 'HP':
        if move.special_move and agent.mp > 0:
            agent_buff = agent.spc_attack_dmg
        else:
            agent_buff = agent.attack_dmg
        magnitude = apply_effect_stat(magnitude,
                                      agent_buff)
    current_value = getattr(entity,
                            target_var)
    setattr(entity,
            target_var,
            current_value + magnitude
            )
    entity.save()
    if move.special_move:
        agent.mp -= 1
        agent.save()
    return magnitude
